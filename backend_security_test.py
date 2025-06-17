import requests
import unittest
import sys
import json
from datetime import datetime

class TRACITYAPISecurityTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.auth_token = None
        self.user_id = None
        self.session_id = None
        self.captcha_answer = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if self.auth_token and 'Authorization' not in headers:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                if files:
                    # For multipart/form-data (file uploads)
                    if 'Content-Type' in headers:
                        del headers['Content-Type']  # Let requests set the correct content type
                    response = requests.post(url, headers=headers, params=params, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers, params=params)

            success = response.status_code == expected_status
            
            result = {
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.status_code != 204:  # No content
                    try:
                        result["response"] = response.json()
                    except:
                        result["response"] = response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    result["error"] = response.json()
                except:
                    result["error"] = response.text
            
            self.test_results.append(result)
            return success, response

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "error": str(e)
            })
            return False, None

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*50)
        print(f"📊 TEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        # Print failed tests
        if self.tests_passed < self.tests_run:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"- {result['name']} ({result['method']} {result['endpoint']})")
                    if "error" in result:
                        print(f"  Error: {result['error']}")
        print("="*50)

class TestTRACITYSecurityIssues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get the backend URL from the environment variable
        cls.base_url = "https://38c5b002-937f-4add-9333-a54cc7abea8a.preview.emergentagent.com/api"
        cls.tester = TRACITYAPISecurityTester(cls.base_url)
        print(f"Testing API at: {cls.base_url}")
        
        # Test user credentials
        cls.test_user = {
            "email": f"security_test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            "password": "SecurePassword123!"
        }

    def test_01_captcha_verification(self):
        """Test if captcha verification is properly enforced"""
        # Get a captcha
        success, response = self.tester.run_test(
            "Get Captcha",
            "GET",
            "captcha",
            200
        )
        self.assertTrue(success)
        
        if success:
            data = response.json()
            self.tester.session_id = data["session_id"]
            
            # Extract the answer from the question
            question = data["question"]
            numbers = [int(s) for s in question.split() if s.isdigit()]
            self.tester.captcha_answer = sum(numbers)
            
            # Try login with incorrect captcha
            login_data = {
                "email": self.test_user["email"],
                "password": self.test_user["password"],
                "captcha_answer": 9999  # Incorrect answer
            }
            
            success, response = self.tester.run_test(
                "Login with Invalid Captcha",
                "POST",
                "login",
                401,  # Should be unauthorized
                data=login_data
            )
            
            # If this test passes, captcha verification is working
            # If it fails, captcha verification is not properly enforced
            if not success:
                print("⚠️ SECURITY ISSUE: Captcha verification is not properly enforced")
                print("The login endpoint accepts invalid captcha answers")
                print("This could allow brute force attacks against user accounts")
                print("Recommendation: Fix the captcha verification in the login endpoint")
            else:
                print("✅ Captcha verification is properly enforced")

    def test_02_upload_authentication(self):
        """Test if upload endpoint properly enforces authentication"""
        # Try upload without authentication
        files = {
            'file': ('security_test.txt', 'Test content', 'text/plain')
        }
        
        # Use a request without authentication
        headers = {}  # No Authorization header
        
        success, response = self.tester.run_test(
            "Upload Without Authentication",
            "POST",
            "upload",
            401,  # Should be unauthorized
            files=files,
            headers=headers
        )
        
        # If this test passes, authentication is properly enforced
        # If it fails, authentication is not properly enforced
        if not success:
            print("⚠️ SECURITY ISSUE: Authentication is not properly enforced on the upload endpoint")
            print("The upload endpoint accepts requests without authentication")
            print("This could allow unauthorized users to upload files")
            print("Recommendation: Fix the authentication check in the upload endpoint")
        else:
            print("✅ Upload endpoint properly enforces authentication")

    def test_03_user_files_authentication(self):
        """Test if user/files endpoint properly enforces authentication"""
        # Try access without authentication
        headers = {}  # No Authorization header
        
        success, response = self.tester.run_test(
            "Access User Files Without Authentication",
            "GET",
            "user/files",
            401,  # Should be unauthorized
            headers=headers
        )
        
        # If this test passes, authentication is properly enforced
        # If it fails, authentication is not properly enforced
        if not success:
            print("⚠️ SECURITY ISSUE: Authentication is not properly enforced on the user/files endpoint")
            print("The user/files endpoint accepts requests without authentication")
            print("This could allow unauthorized access to user file listings")
            print("Recommendation: Fix the authentication check in the user/files endpoint")
        else:
            print("✅ User files endpoint properly enforces authentication")

    def test_04_user_file_data_authentication(self):
        """Test if user/data/{file_id} endpoint properly enforces authentication"""
        # Try access without authentication
        headers = {}  # No Authorization header
        
        success, response = self.tester.run_test(
            "Access User File Data Without Authentication",
            "GET",
            "user/data/some-file-id",
            401,  # Should be unauthorized
            headers=headers
        )
        
        # If this test passes, authentication is properly enforced
        # If it fails, authentication is not properly enforced
        if not success:
            print("⚠️ SECURITY ISSUE: Authentication is not properly enforced on the user/data endpoint")
            print("The user/data endpoint accepts requests without authentication")
            print("This could allow unauthorized access to user file data")
            print("Recommendation: Fix the authentication check in the user/data endpoint")
        else:
            print("✅ User file data endpoint properly enforces authentication")

    @classmethod
    def tearDownClass(cls):
        cls.tester.print_summary()

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)