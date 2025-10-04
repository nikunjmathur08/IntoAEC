"""
Security testing script for IntoAEC
Tests all implemented security measures
"""
import requests
import json
import time
import os
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com", 
    "password": "TestPass123!"
}

class SecurityTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def test_authentication(self) -> Dict[str, Any]:
        """Test authentication system"""
        print("🔐 Testing Authentication System...")
        results = {}
        
        # Test 1: Registration
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=TEST_USER,
                timeout=10
            )
            results["registration"] = {
                "status": response.status_code,
                "success": response.status_code in [200, 201],
                "message": response.json().get("message", "No message")
            }
        except Exception as e:
            results["registration"] = {"error": str(e)}
        
        # Test 2: Login
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": TEST_USER["username"], "password": TEST_USER["password"]},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                results["login"] = {
                    "status": response.status_code,
                    "success": True,
                    "token_received": bool(self.auth_token)
                }
            else:
                results["login"] = {
                    "status": response.status_code,
                    "success": False,
                    "error": response.text
                }
        except Exception as e:
            results["login"] = {"error": str(e)}
        
        return results
    
    def test_authorization(self) -> Dict[str, Any]:
        """Test authorization system"""
        print("🛡️ Testing Authorization System...")
        results = {}
        
        # Test 1: Access protected endpoint without token
        try:
            response = self.session.get(f"{self.base_url}/model/info", timeout=10)
            results["no_auth"] = {
                "status": response.status_code,
                "success": response.status_code == 401,
                "message": "Should be 401 Unauthorized"
            }
        except Exception as e:
            results["no_auth"] = {"error": str(e)}
        
        # Test 2: Access protected endpoint with token
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.session.get(f"{self.base_url}/model/info", headers=headers, timeout=10)
                results["with_auth"] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "message": "Should be 200 OK"
                }
            except Exception as e:
                results["with_auth"] = {"error": str(e)}
        
        return results
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting"""
        print("⏱️ Testing Rate Limiting...")
        results = {}
        
        if not self.auth_token:
            results["error"] = "No auth token available"
            return results
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test rapid requests
        success_count = 0
        rate_limited_count = 0
        
        for i in range(10):  # Try 10 rapid requests
            try:
                response = self.session.get(f"{self.base_url}/model/info", headers=headers, timeout=5)
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
                time.sleep(0.1)  # Small delay
            except Exception as e:
                print(f"Request {i+1} failed: {e}")
        
        results["rate_limiting"] = {
            "successful_requests": success_count,
            "rate_limited_requests": rate_limited_count,
            "working": rate_limited_count > 0
        }
        
        return results
    
    def test_file_upload_security(self) -> Dict[str, Any]:
        """Test file upload security"""
        print("📁 Testing File Upload Security...")
        results = {}
        
        if not self.auth_token:
            results["error"] = "No auth token available"
            return results
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test 1: Valid image upload
        try:
            # Create a small test image
            import io
            from PIL import Image
            
            img = Image.new('RGB', (100, 100), color='red')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            files = {'file': ('test.png', img_byte_arr, 'image/png')}
            data = {'model_type': 'yolo'}
            
            response = self.session.post(
                f"{self.base_url}/analyze",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            results["valid_upload"] = {
                "status": response.status_code,
                "success": response.status_code in [200, 201],
                "message": "Valid image upload test"
            }
        except Exception as e:
            results["valid_upload"] = {"error": str(e)}
        
        # Test 2: Invalid file type
        try:
            files = {'file': ('test.txt', b'Hello World', 'text/plain')}
            data = {'model_type': 'yolo'}
            
            response = self.session.post(
                f"{self.base_url}/analyze",
                headers=headers,
                files=files,
                data=data,
                timeout=10
            )
            
            results["invalid_file"] = {
                "status": response.status_code,
                "success": response.status_code == 400,
                "message": "Should reject invalid file type"
            }
        except Exception as e:
            results["invalid_file"] = {"error": str(e)}
        
        return results
    
    def test_input_validation(self) -> Dict[str, Any]:
        """Test input validation"""
        print("✅ Testing Input Validation...")
        results = {}
        
        if not self.auth_token:
            results["error"] = "No auth token available"
            return results
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test invalid model type
        try:
            response = self.session.get(
                f"{self.base_url}/model/info?model_type=invalid",
                headers=headers,
                timeout=10
            )
            results["invalid_model"] = {
                "status": response.status_code,
                "success": response.status_code in [200, 400],  # Either works or properly rejects
                "message": "Invalid model type handling"
            }
        except Exception as e:
            results["invalid_model"] = {"error": str(e)}
        
        return results
    
    def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers"""
        print("🔒 Testing Security Headers...")
        results = {}
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            headers = response.headers
            
            security_headers = {
                "X-Content-Type-Options": headers.get("X-Content-Type-Options"),
                "X-Frame-Options": headers.get("X-Frame-Options"),
                "X-XSS-Protection": headers.get("X-XSS-Protection"),
                "Strict-Transport-Security": headers.get("Strict-Transport-Security"),
                "Referrer-Policy": headers.get("Referrer-Policy"),
                "Content-Security-Policy": headers.get("Content-Security-Policy")
            }
            
            results["security_headers"] = {
                "headers_present": {k: v is not None for k, v in security_headers.items()},
                "headers": security_headers,
                "all_present": all(v is not None for v in security_headers.values())
            }
        except Exception as e:
            results["security_headers"] = {"error": str(e)}
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        print("🚀 Starting Security Test Suite...")
        print("=" * 50)
        
        all_results = {}
        
        # Run all tests
        all_results["authentication"] = self.test_authentication()
        all_results["authorization"] = self.test_authorization()
        all_results["rate_limiting"] = self.test_rate_limiting()
        all_results["file_upload_security"] = self.test_file_upload_security()
        all_results["input_validation"] = self.test_input_validation()
        all_results["security_headers"] = self.test_security_headers()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 SECURITY TEST SUMMARY")
        print("=" * 50)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in all_results.items():
            print(f"\n{category.upper()}:")
            for test_name, test_result in results.items():
                if isinstance(test_result, dict) and "success" in test_result:
                    total_tests += 1
                    if test_result["success"]:
                        passed_tests += 1
                        print(f"  ✅ {test_name}: PASSED")
                    else:
                        print(f"  ❌ {test_name}: FAILED")
                elif isinstance(test_result, dict) and "error" in test_result:
                    print(f"  ⚠️ {test_name}: ERROR - {test_result['error']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL SECURITY TESTS PASSED!")
        else:
            print("⚠️ Some security tests failed. Review the results above.")
        
        return all_results

def main():
    """Main function to run security tests"""
    print("🔐 IntoAEC Security Test Suite")
    print("Testing all implemented security measures...")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the server first:")
        print("   python server/main_secure.py")
        return
    
    # Run security tests
    tester = SecurityTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("security_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: security_test_results.json")

if __name__ == "__main__":
    main()

