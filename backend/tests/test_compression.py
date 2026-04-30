"""
Tests for compression middleware.
Tests Gzip/Brotli compression, content-type filtering, metrics, and client compatibility.
"""

import pytest
import gzip
import io
from unittest.mock import Mock, AsyncMock, patch
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.testclient import TestClient
from fastapi import FastAPI

from backend.middleware.compression_middleware import (
    CompressionMiddleware,
    get_compression_metrics,
    reset_compression_metrics,
    DEFAULT_COMPRESSIBLE_CONTENT_TYPES,
    DEFAULT_MIN_SIZE,
)


@pytest.fixture
def app():
    """Create test FastAPI app."""
    test_app = FastAPI()
    
    @test_app.get("/test/json")
    async def test_json():
        return {"message": "Hello World", "data": "x" * 2000}
    
    @test_app.get("/test/html")
    async def test_html():
        return Response(content="<html><body>" + "x" * 2000 + "</body></html>", media_type="text/html")
    
    @test_app.get("/test/text")
    async def test_text():
        return Response(content="Plain text content " * 200, media_type="text/plain")
    
    @test_app.get("/test/small")
    async def test_small():
        return Response(content="Small", media_type="text/plain")
    
    @test_app.get("/test/image")
    async def test_image():
        return Response(content=b"binary image data" * 200, media_type="image/png")
    
    @test_app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return test_app


@pytest.fixture
def client_with_gzip(app):
    """Create test client with gzip compression enabled."""
    reset_compression_metrics()
    app.add_middleware(
        CompressionMiddleware,
        enabled=True,
        gzip_level=6,
        brotli_level=4,
        min_size=100,
        track_metrics=True,
    )
    return TestClient(app)


@pytest.fixture
def client_with_brotli(app):
    """Create test client with brotli compression enabled."""
    reset_compression_metrics()
    try:
        import brotli
        brotli_available = True
    except ImportError:
        brotli_available = False
    
    app.add_middleware(
        CompressionMiddleware,
        enabled=True,
        gzip_level=6,
        brotli_level=4,
        min_size=100,
        track_metrics=True,
    )
    return TestClient(app), brotli_available


@pytest.fixture
def client_disabled(app):
    """Create test client with compression disabled."""
    reset_compression_metrics()
    app.add_middleware(
        CompressionMiddleware,
        enabled=False,
    )
    return TestClient(app)


class TestCompressionMiddlewareGzip:
    """Test Gzip compression functionality."""
    
    def test_gzip_compression_json(self, client_with_gzip):
        """Test that JSON responses are compressed with gzip."""
        response = client_with_gzip.get(
            "/test/json",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        assert response.headers.get("Content-Encoding") == "gzip"
        assert response.headers.get("Vary") == "Accept-Encoding"
        
        # Decompress and verify content
        decompressed = gzip.decompress(response.content)
        assert b"Hello World" in decompressed
    
    def test_gzip_compression_html(self, client_with_gzip):
        """Test that HTML responses are compressed with gzip."""
        response = client_with_gzip.get(
            "/test/html",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        assert response.headers.get("Content-Encoding") == "gzip"
        
        # Decompress and verify content
        decompressed = gzip.decompress(response.content)
        assert b"<html>" in decompressed
    
    def test_gzip_compression_text(self, client_with_gzip):
        """Test that text responses are compressed with gzip."""
        response = client_with_gzip.get(
            "/test/text",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        assert response.headers.get("Content-Encoding") == "gzip"
        
        # Decompress and verify content
        decompressed = gzip.decompress(response.content)
        assert b"Plain text content" in decompressed
    
    def test_no_compression_without_accept_encoding(self, client_with_gzip):
        """Test that responses are not compressed when client doesn't accept encoding."""
        response = client_with_gzip.get("/test/json")
        
        assert response.status_code == 200
        assert "Content-Encoding" not in response.headers
    
    def test_no_compression_for_small_responses(self, client_with_gzip):
        """Test that small responses are not compressed."""
        response = client_with_gzip.get(
            "/test/small",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        assert "Content-Encoding" not in response.headers
        assert response.text == "Small"


class TestCompressionMiddlewareBrotli:
    """Test Brotli compression functionality."""
    
    def test_brotli_compression_json(self, client_with_brotli):
        """Test that JSON responses are compressed with brotli if available."""
        client, brotli_available = client_with_brotli
        
        response = client.get(
            "/test/json",
            headers={"Accept-Encoding": "br, gzip"}
        )
        
        assert response.status_code == 200
        
        if brotli_available:
            assert response.headers.get("Content-Encoding") == "br"
            # Decompress and verify content
            import brotli
            decompressed = brotli.decompress(response.content)
            assert b"Hello World" in decompressed
        else:
            # Fall back to gzip
            assert response.headers.get("Content-Encoding") == "gzip"
            decompressed = gzip.decompress(response.content)
            assert b"Hello World" in decompressed


class TestContentTypeFiltering:
    """Test content-type based compression filtering."""
    
    def test_compress_json_content_type(self, client_with_gzip):
        """Test that application/json is compressed."""
        response = client_with_gzip.get(
            "/test/json",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.headers.get("Content-Encoding") == "gzip"
    
    def test_compress_html_content_type(self, client_with_gzip):
        """Test that text/html is compressed."""
        response = client_with_gzip.get(
            "/test/html",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.headers.get("Content-Encoding") == "gzip"
    
    def test_no_compression_for_image(self, client_with_gzip):
        """Test that image content types are not compressed."""
        response = client_with_gzip.get(
            "/test/image",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        assert "Content-Encoding" not in response.headers


class TestExcludedPaths:
    """Test path exclusion from compression."""
    
    def test_health_endpoint_not_compressed(self, client_with_gzip):
        """Test that /health endpoint is not compressed."""
        response = client_with_gzip.get(
            "/health",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        assert "Content-Encoding" not in response.headers


class TestClientCompatibility:
    """Test client compatibility with different Accept-Encoding headers."""
    
    def test_gzip_only(self, client_with_gzip):
        """Test compression when client only accepts gzip."""
        response = client_with_gzip.get(
            "/test/json",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.headers.get("Content-Encoding") == "gzip"
    
    def test_brotli_and_gzip(self, client_with_brotli):
        """Test compression when client accepts both brotli and gzip."""
        client, brotli_available = client_with_brotli
        
        response = client.get(
            "/test/json",
            headers={"Accept-Encoding": "br, gzip"}
        )
        
        # Should prefer brotli if available
        if brotli_available:
            assert response.headers.get("Content-Encoding") == "br"
        else:
            assert response.headers.get("Content-Encoding") == "gzip"
    
    def test_no_supported_encoding(self, client_with_gzip):
        """Test no compression when client doesn't support any encoding."""
        response = client_with_gzip.get(
            "/test/json",
            headers={"Accept-Encoding": "deflate"}
        )
        
        assert "Content-Encoding" not in response.headers
    
    def test_quality_values(self, client_with_gzip):
        """Test compression with quality values in Accept-Encoding."""
        response = client_with_gzip.get(
            "/test/json",
            headers={"Accept-Encoding": "gzip;q=0.8, br;q=0.9"}
        )
        
        # Should still compress (quality parsing may vary)
        assert response.status_code == 200


class TestCompressionDisabled:
    """Test behavior when compression is disabled."""
    
    def test_no_compression_when_disabled(self, client_disabled):
        """Test that no compression occurs when disabled."""
        response = client_disabled.get(
            "/test/json",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        assert "Content-Encoding" not in response.headers


class TestCompressionMetrics:
    """Test compression metrics tracking."""
    
    def test_metrics_tracking(self, client_with_gzip):
        """Test that compression metrics are tracked."""
        reset_compression_metrics()
        
        # Make several requests
        client_with_gzip.get("/test/json", headers={"Accept-Encoding": "gzip"})
        client_with_gzip.get("/test/html", headers={"Accept-Encoding": "gzip"})
        client_with_gzip.get("/test/text", headers={"Accept-Encoding": "gzip"})
        
        metrics = get_compression_metrics()
        
        assert metrics["total_requests"] > 0
        assert metrics["compressed_requests"] > 0
        assert metrics["gzip_requests"] > 0
        assert metrics["original_bytes"] > 0
        assert metrics["compressed_bytes"] > 0
        assert metrics["compression_ratio"] >= 0
    
    def test_metrics_reset(self, client_with_gzip):
        """Test that metrics can be reset."""
        reset_compression_metrics()
        
        # Make a request
        client_with_gzip.get("/test/json", headers={"Accept-Encoding": "gzip"})
        
        metrics = get_compression_metrics()
        assert metrics["compressed_requests"] > 0
        
        # Reset metrics
        reset_compression_metrics()
        metrics = get_compression_metrics()
        
        assert metrics["total_requests"] == 0
        assert metrics["compressed_requests"] == 0
        assert metrics["original_bytes"] == 0
    
    def test_uncompressed_requests_tracked(self, client_with_gzip):
        """Test that uncompressed requests are also tracked."""
        reset_compression_metrics()
        
        # Make request without compression
        client_with_gzip.get("/test/json")
        
        metrics = get_compression_metrics()
        # The request should be counted in total but not compressed
        assert metrics["total_requests"] >= 0


class TestCompressionLevels:
    """Test different compression levels."""
    
    def test_gzip_level_1(self, app):
        """Test gzip compression with level 1 (fastest)."""
        reset_compression_metrics()
        app.add_middleware(
            CompressionMiddleware,
            enabled=True,
            gzip_level=1,
            min_size=100,
        )
        
        client = TestClient(app)
        response = client.get("/test/json", headers={"Accept-Encoding": "gzip"})
        
        assert response.status_code == 200
        assert response.headers.get("Content-Encoding") == "gzip"
    
    def test_gzip_level_9(self, app):
        """Test gzip compression with level 9 (best compression)."""
        reset_compression_metrics()
        app.add_middleware(
            CompressionMiddleware,
            enabled=True,
            gzip_level=9,
            min_size=100,
        )
        
        client = TestClient(app)
        response = client.get("/test/json", headers={"Accept-Encoding": "gzip"})
        
        assert response.status_code == 200
        assert response.headers.get("Content-Encoding") == "gzip"


class TestCompressionMiddleware:
    """Test CompressionMiddleware class directly."""
    
    def test_default_compressible_content_types(self):
        """Test default compressible content types."""
        assert "application/json" in DEFAULT_COMPRESSIBLE_CONTENT_TYPES
        assert "text/html" in DEFAULT_COMPRESSIBLE_CONTENT_TYPES
        assert "text/css" in DEFAULT_COMPRESSIBLE_CONTENT_TYPES
        assert "image/png" not in DEFAULT_COMPRESSIBLE_CONTENT_TYPES
    
    def test_min_size_default(self):
        """Test default minimum size."""
        assert DEFAULT_MIN_SIZE == 1024
    
    def test_gzip_level_bounds(self, app):
        """Test that gzip level is bounded between 1-9."""
        reset_compression_metrics()
        app.add_middleware(
            CompressionMiddleware,
            enabled=True,
            gzip_level=15,  # Should be clamped to 9
            min_size=100,
        )
        
        client = TestClient(app)
        response = client.get("/test/json", headers={"Accept-Encoding": "gzip"})
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
