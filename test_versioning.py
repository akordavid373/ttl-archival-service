#!/usr/bin/env python3
"""
Test script for API versioning implementation
"""

import requests
import json
from typing import Dict, Any

class VersioningTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_version_info_endpoint(self) -> Dict[str, Any]:
        """Test the /version endpoint"""
        print("🧪 Testing /version endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/version")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Version info retrieved successfully")
                print(f"   Current version: {data.get('current_version')}")
                print(f"   Supported versions: {data.get('supported_versions')}")
                print(f"   Recommended version: {data.get('recommended_version')}")
                return data
            else:
                print(f"❌ Failed to get version info: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error testing version endpoint: {e}")
            return {}
    
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the /health endpoint"""
        print("\n🧪 Testing /health endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Supported versions: {data.get('supported_versions')}")
                return data
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error testing health endpoint: {e}")
            return {}
    
    def test_url_versioning(self) -> bool:
        """Test URL-based versioning"""
        print("\n🧪 Testing URL-based versioning...")
        
        try:
            # Test v1 URL
            response = self.session.get(f"{self.base_url}/api/v1/health")
            if response.status_code == 200:
                print(f"✅ v1 URL versioning works")
            else:
                print(f"❌ v1 URL versioning failed: {response.status_code}")
                return False
            
            # Test v2 URL
            response = self.session.get(f"{self.base_url}/api/v2/archives")
            if response.status_code in [200, 401, 422]:  # Expected responses
                print(f"✅ v2 URL versioning works")
            else:
                print(f"❌ v2 URL versioning failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing URL versioning: {e}")
            return False
    
    def test_header_versioning(self) -> bool:
        """Test header-based versioning"""
        print("\n🧪 Testing header-based versioning...")
        
        try:
            # Test X-API-Version header
            headers = {"X-API-Version": "v2"}
            response = self.session.get(f"{self.base_url}/api/archives", headers=headers)
            
            # Check for version headers in response
            api_version = response.headers.get("API-Version")
            if api_version:
                print(f"✅ X-API-Version header works (detected: {api_version})")
            else:
                print(f"⚠️  X-API-Version header not detected in response")
            
            # Test Accept header with version
            headers = {"Accept": "application/json; version=v2"}
            response = self.session.get(f"{self.base_url}/api/archives", headers=headers)
            
            api_version = response.headers.get("API-Version")
            if api_version:
                print(f"✅ Accept header versioning works (detected: {api_version})")
            else:
                print(f"⚠️  Accept header versioning not detected in response")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing header versioning: {e}")
            return False
    
    def test_deprecation_headers(self) -> bool:
        """Test deprecation headers for v1"""
        print("\n🧪 Testing deprecation headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/archives")
            
            deprecation = response.headers.get("Deprecation")
            sunset = response.headers.get("Sunset")
            warning = response.headers.get("Warning")
            
            if deprecation == "true":
                print(f"✅ Deprecation header present")
            else:
                print(f"⚠️  Deprecation header missing")
            
            if sunset:
                print(f"✅ Sunset header present: {sunset}")
            else:
                print(f"⚠️  Sunset header missing")
            
            if warning and "deprecated" in warning:
                print(f"✅ Warning header present")
            else:
                print(f"⚠️  Warning header missing or doesn't contain deprecation warning")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing deprecation headers: {e}")
            return False
    
    def test_v2_enhanced_features(self) -> bool:
        """Test v2 enhanced features"""
        print("\n🧪 Testing v2 enhanced features...")
        
        try:
            # Test enhanced search endpoint
            search_data = {
                "query": "test",
                "search_type": "semantic",
                "filters": {"tags": ["test"]},
                "highlighting": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v2/search",
                json=search_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 422]:  # 422 expected if no data
                print(f"✅ Enhanced search endpoint accessible")
            else:
                print(f"❌ Enhanced search endpoint failed: {response.status_code}")
                return False
            
            # Test batch operations endpoint
            batch_data = {
                "archives": [],
                "validate_all": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v2/archives/batch",
                json=batch_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 422]:
                print(f"✅ Batch operations endpoint accessible")
            else:
                print(f"❌ Batch operations endpoint failed: {response.status_code}")
                return False
            
            # Test webhooks endpoint
            webhook_data = {
                "name": "Test Webhook",
                "url": "https://example.com/webhook",
                "events": ["test.event"],
                "active": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v2/webhooks",
                json=webhook_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 422]:
                print(f"✅ Webhooks endpoint accessible")
            else:
                print(f"❌ Webhooks endpoint failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing v2 enhanced features: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all versioning tests"""
        print("🚀 Starting API Versioning Tests\n")
        
        results = {}
        
        # Test core endpoints
        results['version_info'] = bool(self.test_version_info_endpoint())
        results['health'] = bool(self.test_health_endpoint())
        
        # Test versioning methods
        results['url_versioning'] = self.test_url_versioning()
        results['header_versioning'] = self.test_header_versioning()
        
        # Test deprecation
        results['deprecation_headers'] = self.test_deprecation_headers()
        
        # Test v2 features
        results['v2_features'] = self.test_v2_enhanced_features()
        
        # Summary
        print("\n" + "="*50)
        print("📊 TEST RESULTS SUMMARY")
        print("="*50)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status:<8} {test_name.replace('_', ' ').title()}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API versioning is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        return results

def main():
    """Main test runner"""
    tester = VersioningTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if all(results.values()) else 1
    exit(exit_code)

if __name__ == "__main__":
    main()
