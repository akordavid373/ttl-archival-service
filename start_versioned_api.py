#!/usr/bin/env python3
"""
Startup script for the versioned TTL Archival Service API
"""

import uvicorn
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    """Start the versioned API server"""
    print("🚀 Starting TTL Archival Service with API Versioning...")
    print("📋 Versioning Features:")
    print("   ✅ URL-based versioning (/api/v1/, /api/v2/)")
    print("   ✅ Header-based versioning (X-API-Version, Accept)")
    print("   ✅ Deprecation warnings and headers")
    print("   ✅ Version negotiation middleware")
    print("   ✅ Enhanced v2 features (batch ops, webhooks, notifications)")
    print()
    print("🌐 Available endpoints:")
    print("   📖 Version Info: http://localhost:8000/version")
    print("   💚 Health Check: http://localhost:8000/health")
    print("   📚 API Docs: http://localhost:8000/docs")
    print("   🧪 Test Script: python test_versioning.py")
    print()
    print("🔧 Version Examples:")
    print("   v1 (deprecated): http://localhost:8000/api/v1/archives")
    print("   v2 (current):   http://localhost:8000/api/v2/archives")
    print()
    
    try:
        # Start the server
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
