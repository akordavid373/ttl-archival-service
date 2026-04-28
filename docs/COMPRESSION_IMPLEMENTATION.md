# Response Compression Implementation

## Overview

This implementation adds comprehensive response compression to the TTL Archival Service to reduce bandwidth usage and improve API performance. The compression system supports both **Gzip** and **Brotli** compression algorithms with full configurability.

## Features Implemented

✅ **Gzip/Brotli Compression** - Dual algorithm support with automatic fallback  
✅ **Compression Level Configuration** - Configurable compression levels for both algorithms  
✅ **Content-type Based Compression** - Smart filtering based on response content type  
✅ **Compression Metrics** - Real-time tracking of compression performance  
✅ **Client Compatibility** - Respects `Accept-Encoding` headers and quality values  

## Architecture

### Components

1. **CompressionMiddleware** (`backend/middleware/compression_middleware.py`)
   - Core middleware implementation
   - Handles compression algorithm selection
   - Manages content-type filtering
   - Tracks compression metrics

2. **Configuration** (`backend/config/settings.py`)
   - `CompressionConfig` dataclass
   - Environment variable support
   - Runtime configuration updates

3. **Metrics System**
   - Global metrics store with thread-safe access
   - Real-time compression statistics
   - API endpoints for metrics retrieval

4. **Integration** (`backend/main.py`)
   - Middleware registration
   - Metrics endpoints
   - Configuration loading

## Configuration

### Environment Variables

Add these to your `.env` file (see `.env.example`):

```bash
# Response Compression
COMPRESSION_ENABLED=true
COMPRESSION_GZIP_LEVEL=6
COMPRESSION_BROTLI_LEVEL=4
COMPRESSION_MIN_SIZE=1024
COMPRESSION_TRACK_METRICS=true
COMPRESSION_CONTENT_TYPES=text/html,text/css,text/plain,text/xml,text/javascript,application/json,application/javascript,application/xml,application/xhtml+xml,application/rss+xml,application/atom+xml,image/svg+xml,font/woff,font/woff2
COMPRESSION_EXCLUDE_PATHS=/health,/metrics,/docs,/openapi.json,/redoc
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `COMPRESSION_ENABLED` | bool | `true` | Enable/disable compression |
| `COMPRESSION_GZIP_LEVEL` | int (1-9) | `6` | Gzip compression level (1=fastest, 9=best) |
| `COMPRESSION_BROTLI_LEVEL` | int (0-11) | `4` | Brotli compression level (0=fastest, 11=best) |
| `COMPRESSION_MIN_SIZE` | int | `1024` | Minimum response size in bytes to compress |
| `COMPRESSION_TRACK_METRICS` | bool | `true` | Enable compression metrics tracking |
| `COMPRESSION_CONTENT_TYPES` | string | (see above) | Comma-separated list of compressible content types |
| `COMPRESSION_EXCLUDE_PATHS` | string | (see above) | Comma-separated list of paths to exclude |

## API Endpoints

### Get Compression Metrics

```http
GET /api/v1/monitoring/compression-metrics
```

**Response:**
```json
{
  "total_requests": 150,
  "compressed_requests": 120,
  "gzip_requests": 100,
  "brotli_requests": 20,
  "uncompressed_requests": 30,
  "original_bytes": 5242880,
  "compressed_bytes": 1572864,
  "errors": 0,
  "compression_ratio": 70.0,
  "compression_rate": 80.0,
  "timestamp": 1714406400.0
}
```

### Reset Compression Metrics

```http
POST /api/v1/monitoring/compression-metrics/reset
```

**Response:**
```json
{
  "message": "Compression metrics reset successfully"
}
```

## Usage Examples

### Client Request with Gzip

```bash
curl -H "Accept-Encoding: gzip" http://localhost:8000/api/v1/archives
```

**Response Headers:**
```
Content-Encoding: gzip
Content-Length: 15234
Vary: Accept-Encoding
```

### Client Request with Brotli (Preferred)

```bash
curl -H "Accept-Encoding: br, gzip" http://localhost:8000/api/v1/archives
```

**Response Headers:**
```
Content-Encoding: br
Content-Length: 12456
Vary: Accept-Encoding
```

### Client Request without Compression Support

```bash
curl http://localhost:8000/api/v1/archives
```

**Response:** Uncompressed (no `Content-Encoding` header)

## Algorithm Selection

The middleware selects compression algorithms based on:

1. **Client Support**: Checks `Accept-Encoding` header
2. **Availability**: Brotli requires `brotli` package
3. **Priority**: Brotli > Gzip (when both available)

**Priority Order:**
1. Brotli (if client supports and package installed)
2. Gzip (if client supports)
3. No compression (fallback)

## Content-Type Filtering

### Compressible Types (Default)

- `text/html`
- `text/css`
- `text/plain`
- `text/xml`
- `text/javascript`
- `application/json`
- `application/javascript`
- `application/xml`
- `application/xhtml+xml`
- `application/rss+xml`
- `application/atom+xml`
- `image/svg+xml`
- `font/woff`
- `font/woff2`

### Non-Compressible Types

- Images (PNG, JPEG, GIF, etc.) - Already compressed
- Videos (MP4, WebM, etc.) - Already compressed
- Archives (ZIP, RAR, etc.) - Already compressed
- Binary files

## Performance Considerations

### Compression Levels

**Gzip Levels:**
- **1-3**: Fast compression, larger output (good for high-traffic APIs)
- **4-6**: Balanced compression and speed (default: 6)
- **7-9**: Best compression, slower (good for static content)

**Brotli Levels:**
- **0-3**: Fast compression
- **4-6**: Balanced (default: 4)
- **7-9**: Better compression
- **10-11**: Best compression (CPU intensive)

### Minimum Size Threshold

The `COMPRESSION_MIN_SIZE` setting (default: 1024 bytes) prevents compression of small responses where:
- Compression overhead exceeds bandwidth savings
- CPU cost isn't justified
- Response might actually get larger

### Excluded Paths

By default, these paths are excluded:
- `/health` - Health checks (frequent, small responses)
- `/metrics` - Metrics endpoints (already optimized)
- `/docs`, `/openapi.json`, `/redoc` - API documentation

## Metrics Explained

### Key Metrics

- **total_requests**: Total requests processed by middleware
- **compressed_requests**: Requests that were compressed
- **gzip_requests**: Requests compressed with Gzip
- **brotli_requests**: Requests compressed with Brotli
- **uncompressed_requests**: Requests not compressed
- **original_bytes**: Total size before compression
- **compressed_bytes**: Total size after compression
- **compression_ratio**: Percentage size reduction ((original - compressed) / original * 100)
- **compression_rate**: Percentage of requests compressed (compressed / total * 100)
- **errors**: Compression failures

### Example Interpretation

```json
{
  "compression_ratio": 70.0,
  "compression_rate": 80.0
}
```

- **70% compression ratio**: Compressed responses are 70% smaller than original
- **80% compression rate**: 80% of eligible requests were compressed

## Installation

### Install Brotli (Optional but Recommended)

```bash
pip install brotli==1.1.0
```

Or install all dependencies:

```bash
pip install -r backend/requirements.txt
```

**Note:** The system works with Gzip only if Brotli is not installed.

## Testing

Run the compression test suite:

```bash
pytest backend/tests/test_compression.py -v
```

### Test Coverage

- ✅ Gzip compression for JSON, HTML, text
- ✅ Brotli compression (when available)
- ✅ Content-type filtering
- ✅ Minimum size threshold
- ✅ Client compatibility (Accept-Encoding)
- ✅ Quality value parsing
- ✅ Excluded paths
- ✅ Compression disabled mode
- ✅ Metrics tracking and reset
- ✅ Compression level bounds
- ✅ Algorithm selection priority

## Troubleshooting

### Issue: No Compression Applied

**Possible Causes:**
1. Client doesn't send `Accept-Encoding` header
2. Response size below `COMPRESSION_MIN_SIZE`
3. Content-type not in compressible list
4. Path is in exclusion list
5. `COMPRESSION_ENABLED=false`

**Solution:**
- Check request headers include `Accept-Encoding: gzip` or `br`
- Verify response size > `COMPRESSION_MIN_SIZE`
- Review `COMPRESSION_CONTENT_TYPES` configuration
- Check `COMPRESSION_EXCLUDE_PATHS` configuration

### Issue: Brotli Not Working

**Possible Causes:**
1. `brotli` package not installed
2. Client doesn't support Brotli

**Solution:**
```bash
pip install brotli
```

Check logs for: `"Brotli compression available"` vs `"Brotli not available, falling back to gzip only"`

### Issue: High CPU Usage

**Possible Causes:**
1. Compression level too high
2. High traffic volume

**Solution:**
- Lower `COMPRESSION_GZIP_LEVEL` (try 4-5)
- Lower `COMPRESSION_BROTLI_LEVEL` (try 2-3)
- Increase `COMPRESSION_MIN_SIZE` to skip small responses

## Best Practices

1. **Enable Brotli**: Install `brotli` package for better compression ratios (15-25% better than Gzip)

2. **Monitor Metrics**: Regularly check `/api/v1/monitoring/compression-metrics` to track performance

3. **Tune Compression Levels**:
   - High-traffic APIs: Use levels 4-6 for balance
   - Low-traffic APIs: Use levels 7-9 for best compression
   - Real-time APIs: Use levels 1-3 for speed

4. **Set Appropriate Min Size**: 1024 bytes is good for most APIs, adjust based on your response sizes

5. **Exclude Health Checks**: Always exclude health check endpoints to reduce overhead

6. **Use CDN**: If using a CDN, compression might be handled at the edge - disable server compression to avoid double compression

## Future Enhancements

Potential improvements for future versions:

- [ ] Dynamic compression level adjustment based on server load
- [ ] Per-endpoint compression configuration
- [ ] Compression caching for repeated responses
- [ ] Zstandard (zstd) compression support
- [ ] Real-time compression dashboard
- [ ] A/B testing for compression levels
- [ ] Compression analytics and reporting

## Acceptance Criteria Checklist

- ✅ **Gzip/Brotli compression**: Both algorithms implemented with automatic selection
- ✅ **Compression level configuration**: Configurable via environment variables (gzip 1-9, brotli 0-11)
- ✅ **Content-type based compression**: Smart filtering with configurable content types
- ✅ **Compression metrics**: Real-time metrics with ratio, rate, and byte tracking
- ✅ **Client compatibility**: Full `Accept-Encoding` header support with quality values

## Dependencies

- **Required**: `fastapi`, `starlette` (already in project)
- **Optional**: `brotli==1.1.0` (recommended for better compression)

## Files Modified/Created

### Created Files
- `backend/middleware/compression_middleware.py` - Core middleware implementation
- `backend/tests/test_compression.py` - Comprehensive test suite

### Modified Files
- `backend/config/settings.py` - Added `CompressionConfig` dataclass
- `backend/main.py` - Integrated compression middleware and metrics endpoints
- `backend/middleware/__init__.py` - Added CompressionMiddleware export
- `backend/requirements.txt` - Added brotli dependency
- `.env.example` - Added compression configuration variables

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review compression metrics at `/api/v1/monitoring/compression-metrics`
3. Check application logs for compression-related warnings
4. Verify client sends proper `Accept-Encoding` headers

---

**Implementation Date**: 2026-04-29  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
