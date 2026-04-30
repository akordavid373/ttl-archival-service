"""
Response compression middleware for TTL archival service.
Supports Gzip and Brotli compression with configurable settings.
"""

import gzip
import io
import time
import threading
import logging
from typing import List, Optional, Set
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

# Global compression metrics store
_compression_metrics = {
    "total_requests": 0,
    "compressed_requests": 0,
    "gzip_requests": 0,
    "brotli_requests": 0,
    "uncompressed_requests": 0,
    "original_bytes": 0,
    "compressed_bytes": 0,
    "errors": 0,
}
_metrics_lock = threading.Lock() if 'threading' in dir() else None


def get_compression_metrics() -> dict:
    """Get global compression metrics."""
    with _metrics_lock:
        metrics = _compression_metrics.copy()
    
    # Calculate compression ratio
    if metrics["original_bytes"] > 0:
        metrics["compression_ratio"] = (
            (metrics["original_bytes"] - metrics["compressed_bytes"]) / 
            metrics["original_bytes"] * 100
        )
    else:
        metrics["compression_ratio"] = 0
    
    # Calculate compression rate
    if metrics["total_requests"] > 0:
        metrics["compression_rate"] = (
            metrics["compressed_requests"] / metrics["total_requests"] * 100
        )
    else:
        metrics["compression_rate"] = 0
    
    metrics["timestamp"] = time.time()
    return metrics


def reset_compression_metrics():
    """Reset global compression metrics."""
    global _compression_metrics
    with _metrics_lock:
        _compression_metrics = {
            "total_requests": 0,
            "compressed_requests": 0,
            "gzip_requests": 0,
            "brotli_requests": 0,
            "uncompressed_requests": 0,
            "original_bytes": 0,
            "compressed_bytes": 0,
            "errors": 0,
        }

# Default compressible content types
DEFAULT_COMPRESSIBLE_CONTENT_TYPES = {
    "text/html",
    "text/css",
    "text/plain",
    "text/xml",
    "text/javascript",
    "application/json",
    "application/javascript",
    "application/xml",
    "application/xhtml+xml",
    "application/rss+xml",
    "application/atom+xml",
    "image/svg+xml",
    "font/woff",
    "font/woff2",
}

# Default minimum size for compression (1024 bytes)
DEFAULT_MIN_SIZE = 1024


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for compressing HTTP responses using Gzip or Brotli.
    
    Features:
    - Supports both Gzip and Brotli compression algorithms
    - Content-type based compression filtering
    - Configurable compression levels
    - Client compatibility via Accept-Encoding header
    - Compression metrics tracking
    - Minimum size threshold to avoid compressing small responses
    """
    
    def __init__(
        self,
        app: ASGIApp,
        enabled: bool = True,
        gzip_level: int = 6,
        brotli_level: int = 4,
        compressible_content_types: Optional[Set[str]] = None,
        min_size: int = DEFAULT_MIN_SIZE,
        exclude_paths: Optional[List[str]] = None,
        track_metrics: bool = True,
    ):
        """
        Initialize compression middleware.
        
        Args:
            app: ASGI application
            enabled: Whether compression is enabled
            gzip_level: Gzip compression level (1-9, default 6)
            brotli_level: Brotli compression level (0-11, default 4)
            compressible_content_types: Set of content types to compress
            min_size: Minimum response size in bytes to compress
            exclude_paths: List of paths to exclude from compression
            track_metrics: Whether to track compression metrics
        """
        super().__init__(app)
        self.enabled = enabled
        self.gzip_level = min(max(gzip_level, 1), 9)
        self.brotli_level = min(max(brotli_level, 0), 11)
        self.compressible_content_types = compressible_content_types or DEFAULT_COMPRESSIBLE_CONTENT_TYPES
        self.min_size = min_size
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/openapi.json", "/redoc"]
        self.track_metrics = track_metrics
        
        # Try to import brotli
        self.brotli_available = False
        try:
            import brotli
            self.brotli_available = True
            logger.info("Brotli compression available")
        except ImportError:
            logger.warning("Brotli not available, falling back to gzip only. Install with: pip install brotli")
        
        # Metrics tracking
        self.metrics = {
            "total_requests": 0,
            "compressed_requests": 0,
            "gzip_requests": 0,
            "brotli_requests": 0,
            "uncompressed_requests": 0,
            "original_bytes": 0,
            "compressed_bytes": 0,
            "errors": 0,
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and compress response if applicable."""
        # Skip compression if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip compression for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Check if client supports compression
        accept_encoding = request.headers.get("accept-encoding", "")
        supported_encodings = self._parse_accept_encoding(accept_encoding)
        
        if not supported_encodings:
            return await call_next(request)
        
        # Process the request
        response = await call_next(request)
        
        # Check if response should be compressed
        if not self._should_compress(response):
            return response
        
        # Select best compression algorithm
        encoding = self._select_encoding(supported_encodings)
        if not encoding:
            return response
        
        # Compress the response
        try:
            compressed_response = await self._compress_response(response, encoding)
            
            # Update metrics
            if self.track_metrics:
                self._update_metrics(encoding, response, compressed_response)
            
            return compressed_response
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            if self.track_metrics:
                self.metrics["errors"] += 1
            # Return original response if compression fails
            return response
    
    def _parse_accept_encoding(self, accept_encoding: str) -> List[str]:
        """
        Parse Accept-Encoding header and return list of supported encodings.
        
        Args:
            accept_encoding: Accept-Encoding header value
            
        Returns:
            List of supported encoding algorithms
        """
        if not accept_encoding:
            return []
        
        encodings = []
        for part in accept_encoding.split(","):
            part = part.strip()
            if ";" in part:
                encoding, quality = part.split(";", 1)
                encoding = encoding.strip().lower()
                # Parse quality value (q=0.8)
                if "q=" in quality:
                    try:
                        q_value = float(quality.split("q=")[1].strip())
                        if q_value > 0:
                            encodings.append((encoding, q_value))
                    except ValueError:
                        encodings.append((encoding, 1.0))
                else:
                    encodings.append((encoding, 1.0))
            else:
                encodings.append((part.lower(), 1.0))
        
        # Sort by quality value (descending)
        encodings.sort(key=lambda x: x[1], reverse=True)
        return [enc[0] for enc in encodings]
    
    def _should_compress(self, response: Response) -> bool:
        """
        Check if response should be compressed.
        
        Args:
            response: HTTP response
            
        Returns:
            True if response should be compressed
        """
        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
        if content_type not in self.compressible_content_types:
            return False
        
        # Check if already encoded
        content_encoding = response.headers.get("content-encoding", "")
        if content_encoding:
            return False
        
        # Check content length (if available)
        content_length = response.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) < self.min_size:
                    return False
            except ValueError:
                pass
        
        return True
    
    def _select_encoding(self, supported_encodings: List[str]) -> Optional[str]:
        """
        Select the best compression encoding based on client support.
        
        Priority: brotli > gzip
        
        Args:
            supported_encodings: List of encodings supported by client
            
        Returns:
            Selected encoding or None
        """
        # Prefer brotli if available and supported
        if "br" in supported_encodings and self.brotli_available:
            return "br"
        
        # Fall back to gzip
        if "gzip" in supported_encodings:
            return "gzip"
        
        return None
    
    async def _compress_response(self, response: Response, encoding: str) -> Response:
        """
        Compress response body with specified encoding.
        
        Args:
            response: Original HTTP response
            encoding: Compression encoding (gzip or br)
            
        Returns:
            Compressed HTTP response
        """
        # Get response body
        body = b""
        if hasattr(response, 'body'):
            body = response.body if isinstance(response.body, bytes) else response.body.encode('utf-8')
        elif hasattr(response, 'body_iterator'):
            async for chunk in response.body_iterator:
                body += chunk if isinstance(chunk, bytes) else chunk.encode('utf-8')
        
        # Check minimum size
        if len(body) < self.min_size:
            return response
        
        # Compress body
        if encoding == "gzip":
            compressed_body = self._compress_gzip(body)
        elif encoding == "br":
            compressed_body = self._compress_brotli(body)
        else:
            return response
        
        # Create new response with compressed body
        response.headers["Content-Encoding"] = encoding
        response.headers["Content-Length"] = str(len(compressed_body))
        response.headers["Vary"] = "Accept-Encoding"
        
        # Create new response with compressed body
        new_response = Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
        
        return new_response
    
    def _compress_gzip(self, data: bytes) -> bytes:
        """
        Compress data using gzip.
        
        Args:
            data: Data to compress
            
        Returns:
            Compressed data
        """
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=self.gzip_level) as f:
            f.write(data)
        return buf.getvalue()
    
    def _compress_brotli(self, data: bytes) -> bytes:
        """
        Compress data using brotli.
        
        Args:
            data: Data to compress
            
        Returns:
            Compressed data
        """
        import brotli
        return brotli.compress(data, quality=self.brotli_level)
    
    def _update_metrics(self, encoding: str, original_response: Response, compressed_response: Response):
        """
        Update compression metrics.
        
        Args:
            encoding: Compression encoding used
            original_response: Original response
            compressed_response: Compressed response
        """
        global _compression_metrics
        
        with _metrics_lock:
            _compression_metrics["total_requests"] += 1
            _compression_metrics["compressed_requests"] += 1
            
            if encoding == "gzip":
                _compression_metrics["gzip_requests"] += 1
            elif encoding == "br":
                _compression_metrics["brotli_requests"] += 1
            
            # Track bytes
            original_size = int(original_response.headers.get("content-length", 0))
            compressed_size = int(compressed_response.headers.get("content-length", 0))
            
            _compression_metrics["original_bytes"] += original_size
            _compression_metrics["compressed_bytes"] += compressed_size
    
    def get_metrics(self) -> dict:
        """
        Get compression metrics.
        
        Returns:
            Dictionary with compression metrics
        """
        return get_compression_metrics()
    
    def reset_metrics(self):
        """Reset compression metrics."""
        reset_compression_metrics()
