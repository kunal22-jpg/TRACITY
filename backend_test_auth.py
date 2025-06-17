import requests
import unittest
import sys
import json
import os
import io
import pandas as pd
from datetime import datetime
import csv
import time

class TRACITYAuthTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.token = None
        self.user_id = None
        self.email = None
        self.file_id = None
        self.filename = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None, auth=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add authorization header if required and token is available
        if auth and self.token:
            headers['Authorization'] = f"Bearer {self.token}"
            print(f"Using token: {self.token[:10]}...")
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                if files:
                    # For file uploads, don't use JSON content type
                    headers.pop('Content-Type', None)
                    response = requests.post(url, headers=headers, files=files)
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

    def create_test_csv(self, filename="test_data.csv"):
        """Create a test CSV file for upload testing"""
        data = [
            {"name": "John Doe", "age": 30, "city": "Mumbai", "income": 75000},
            {"name": "Jane Smith", "age": 25, "city": "Delhi", "income": 65000},
            {"name": "Bob Johnson", "age": 35, "city": "Bangalore", "income": 85000},
            {"name": "Alice Brown", "age": 28, "city": "Chennai", "income": 70000},
            {"name": "Charlie Wilson", "age": 40, "city": "Kolkata", "income": 90000}
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ["name", "age", "city", "income"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        return filename

    def create_test_json(self, filename="test_data.json"):
        """Create a test JSON file for upload testing"""
        data = [
            {"name": "John Doe", "age": 30, "city": "Mumbai", "income": 75000},
            {"name": "Jane Smith", "age": 25, "city": "Delhi", "income": 65000},
            {"name": "Bob Johnson", "age": 35, "city": "Bangalore", "income": 85000},
            {"name": "Alice Brown", "age": 28, "city": "Chennai", "income": 70000},
            {"name": "Charlie Wilson", "age": 40, "city": "Kolkata", "income": 90000}
        ]
        
        with open(filename, 'w') as jsonfile:
            json.dump(data, jsonfile)
        
        return filename

class TestTRACITYAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get the backend URL from the environment variable
        cls.base_url = "https://38c5b002-937f-4add-9333-a54cc7abea8a.preview.emergentagent.com/api"
        cls.tester = TRACITYAuthTester(cls.base_url)
        print(f"Testing API at: {cls.base_url}")
        
        # Test user credentials
        cls.test_email = f"test.user{int(time.time())}@example.com"  # Use timestamp to ensure uniqueness
        cls.test_password = "SecurePassword123!"

    def test_01_captcha_endpoint(self):
        """Test the captcha generation endpoint"""
        success, response = self.tester.run_test(
            "Captcha Generation",
            "GET",
            "captcha",
            200
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("question", data)
            self.assertIn("session_id", data)
            print(f"Captcha Question: {data['question']}")
            print(f"Session ID: {data['session_id']}")
            
            # Extract the numbers from the question to calculate the answer
            import re
            numbers = re.findall(r'\d+', data['question'])
            if len(numbers) == 2:
                captcha_answer = int(numbers[0]) + int(numbers[1])
                print(f"Calculated Captcha Answer: {captcha_answer}")
                
                # Store for login test
                self.captcha_answer = captcha_answer
                self.session_id = data['session_id']

    def test_02_user_registration_login(self):
        """Test user registration and login with captcha"""
        success, response = self.tester.run_test(
            "User Registration/Login",
            "POST",
            "login",
            200,
            data={
                "email": self.test_email,
                "password": self.test_password,
                "captcha_answer": self.captcha_answer
            }
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("token", data)
            self.assertIn("user_id", data)
            self.assertIn("email", data)
            self.assertIn("message", data)
            
            print(f"Login Response: {data['message']}")
            print(f"User ID: {data['user_id']}")
            print(f"Email: {data['email']}")
            
            # Store token and user_id for subsequent tests
            self.tester.token = data['token']
            self.tester.user_id = data['user_id']
            self.tester.email = data['email']

    def test_03_csv_file_upload(self):
        """Test CSV file upload functionality"""
        # Create a test CSV file
        csv_filename = self.tester.create_test_csv()
        
        with open(csv_filename, 'rb') as f:
            files = {'file': (csv_filename, f, 'text/csv')}
            success, response = self.tester.run_test(
                "CSV File Upload",
                "POST",
                "upload",
                200,
                files=files,
                auth=True
            )
        
        # Clean up the test file
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
        
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("file_id", data)
            self.assertIn("filename", data)
            self.assertIn("record_count", data)
            self.assertIn("message", data)
            
            print(f"Upload Response: {data['message']}")
            print(f"File ID: {data['file_id']}")
            print(f"Filename: {data['filename']}")
            print(f"Record Count: {data['record_count']}")
            
            # Store file_id for subsequent tests
            self.tester.file_id = data['file_id']
            self.tester.filename = data['filename']
            
            # Verify record count matches our test data
            self.assertEqual(data['record_count'], 5, "Record count should match the number of rows in test CSV")

    def test_04_json_file_upload(self):
        """Test JSON file upload functionality"""
        # Create a test JSON file
        json_filename = self.tester.create_test_json()
        
        with open(json_filename, 'rb') as f:
            files = {'file': (json_filename, f, 'application/json')}
            success, response = self.tester.run_test(
                "JSON File Upload",
                "POST",
                "upload",
                200,
                files=files,
                auth=True
            )
        
        # Clean up the test file
        if os.path.exists(json_filename):
            os.remove(json_filename)
        
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("file_id", data)
            self.assertIn("filename", data)
            self.assertIn("record_count", data)
            self.assertIn("message", data)
            
            print(f"Upload Response: {data['message']}")
            print(f"File ID: {data['file_id']}")
            print(f"Filename: {data['filename']}")
            print(f"Record Count: {data['record_count']}")
            
            # Store JSON file_id for subsequent tests if needed
            self.json_file_id = data['file_id']
            
            # Verify record count matches our test data
            self.assertEqual(data['record_count'], 5, "Record count should match the number of items in test JSON")

    def test_05_get_user_files(self):
        """Test retrieving user's uploaded files"""
        success, response = self.tester.run_test(
            "Get User Files",
            "GET",
            "user/files",
            200,
            auth=True
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("user_id", data)
            self.assertIn("files", data)
            self.assertIn("total_files", data)
            
            print(f"User ID: {data['user_id']}")
            print(f"Total Files: {data['total_files']}")
            
            # Verify the user_id matches
            self.assertEqual(data['user_id'], self.tester.user_id)
            
            # Verify we have at least the files we uploaded
            self.assertGreaterEqual(data['total_files'], 2, "Should have at least 2 files (CSV and JSON)")
            
            # Verify file details
            for file in data['files']:
                self.assertIn("file_id", file)
                self.assertIn("filename", file)
                self.assertIn("upload_date", file)
                self.assertIn("record_count", file)
                self.assertIn("file_type", file)
                print(f"- {file['filename']} ({file['file_type']}): {file['record_count']} records")

    def test_07_get_file_data(self):
        """Test retrieving data from a specific user file"""
        if not self.tester.file_id:
            self.skipTest("No file_id available from previous tests")
        
        success, response = self.tester.run_test(
            "Get File Data",
            "GET",
            f"user/data/{self.tester.file_id}",
            200,
            auth=True
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("file_id", data)
            self.assertIn("filename", data)
            self.assertIn("data", data)
            self.assertIn("record_count", data)
            
            print(f"File ID: {data['file_id']}")
            print(f"Filename: {data['filename']}")
            print(f"Record Count: {data['record_count']}")
            
            # Verify file_id matches
            self.assertEqual(data['file_id'], self.tester.file_id)
            
            # Verify data structure
            self.assertIsInstance(data['data'], list)
            if data['data']:
                print(f"Sample record: {data['data'][0]}")
                
                # Verify our test data fields are present
                sample = data['data'][0]
                self.assertIn("name", sample)
                self.assertIn("age", sample)
                self.assertIn("city", sample)
                self.assertIn("income", sample)

    def test_08_chat_with_user_data(self):
        """Test chat endpoint with user_id parameter to include user data"""
        if not self.tester.user_id:
            self.skipTest("No user_id available from previous tests")
        
        success, response = self.tester.run_test(
            "Chat With User Data",
            "POST",
            "chat",
            200,
            data={
                "query": "Show me my uploaded data",
                "user_id": self.tester.user_id
            }
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("query", data)
            self.assertIn("results", data)
            
            print(f"Query: {data['query']}")
            print(f"Results Count: {len(data['results'])}")
            
            # Check if user data is included in results
            user_data_found = False
            for result in data['results']:
                if 'is_user_data' in result and result['is_user_data']:
                    user_data_found = True
                    print(f"User data found in results: {result['collection']}")
                    print(f"Insight: {result['insight'][:100]}...")
                    
                    # Verify user data structure
                    self.assertIn("data", result)
                    self.assertIn("record_count", result)
            
            self.assertTrue(user_data_found, "User data should be included in chat results")

    def test_09_chat_without_user_id(self):
        """Test chat endpoint without user_id parameter"""
        success, response = self.tester.run_test(
            "Chat Without User ID",
            "POST",
            "chat",
            200,
            data={
                "query": "Show me crime statistics"
            }
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("query", data)
            self.assertIn("results", data)
            
            print(f"Query: {data['query']}")
            print(f"Results Count: {len(data['results'])}")
            
            # Verify results structure
            for result in data['results']:
                self.assertIn("collection", result)
                self.assertIn("insight", result)
                print(f"Collection: {result['collection']}")
                print(f"Insight: {result['insight'][:100]}...")

    def test_10_unauthorized_file_access(self):
        """Test accessing user files without authentication"""
        success, response = self.tester.run_test(
            "Unauthorized File Access",
            "GET",
            "user/files",
            401,  # Expecting unauthorized
            auth=False  # Explicitly not using auth
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("detail", data)
            print(f"Error Message: {data['detail']}")

    def test_11_invalid_token_access(self):
        """Test accessing protected endpoints with invalid token"""
        # Save the real token and replace with invalid one
        real_token = self.tester.token
        self.tester.token = "invalid_token_12345"
        
        success, response = self.tester.run_test(
            "Invalid Token Access",
            "GET",
            "user/files",
            401,  # Expecting unauthorized
            auth=True
        )
        
        # Restore the real token
        self.tester.token = real_token
        
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("detail", data)
            print(f"Error Message: {data['detail']}")

    def test_12_logout(self):
        """Test user logout functionality"""
        if not self.tester.token:
            self.skipTest("No token available from previous tests")
        
        success, response = self.tester.run_test(
            "User Logout",
            "POST",
            "logout",
            200,
            auth=True
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("message", data)
            print(f"Logout Response: {data['message']}")
            
            # Verify token is invalidated by trying to access a protected endpoint
            success2, response2 = self.tester.run_test(
                "Access After Logout",
                "GET",
                "user/files",
                401,  # Expecting unauthorized
                auth=True  # Using the now-invalid token
            )
            self.assertTrue(success2)
            if success2:
                data2 = response2.json()
                self.assertIn("detail", data2)
                print(f"Post-Logout Access Error: {data2['detail']}")

    def test_13_integration_full_flow(self):
        """Test the complete user flow: login → upload → retrieve → chat"""
        # Step 1: Get a new captcha
        success1, response1 = self.tester.run_test(
            "Integration - Captcha",
            "GET",
            "captcha",
            200
        )
        self.assertTrue(success1)
        if not success1:
            self.skipTest("Failed to get captcha for integration test")
        
        captcha_data = response1.json()
        import re
        numbers = re.findall(r'\d+', captcha_data['question'])
        captcha_answer = int(numbers[0]) + int(numbers[1])
        
        # Step 2: Login with new user
        integration_email = f"integration.test{int(time.time())}@example.com"
        success2, response2 = self.tester.run_test(
            "Integration - Login",
            "POST",
            "login",
            200,
            data={
                "email": integration_email,
                "password": "IntegrationTest123!",
                "captcha_answer": captcha_answer
            }
        )
        self.assertTrue(success2)
        if not success2:
            self.skipTest("Failed to login for integration test")
        
        login_data = response2.json()
        integration_token = login_data['token']
        integration_user_id = login_data['user_id']
        
        # Update tester with new credentials
        self.tester.token = integration_token
        self.tester.user_id = integration_user_id
        
        # Step 3: Upload a file
        csv_filename = self.tester.create_test_csv("integration_test.csv")
        with open(csv_filename, 'rb') as f:
            files = {'file': (csv_filename, f, 'text/csv')}
            success3, response3 = self.tester.run_test(
                "Integration - Upload",
                "POST",
                "upload",
                200,
                files=files,
                auth=True
            )
        
        # Clean up the test file
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
        
        self.assertTrue(success3)
        if not success3:
            self.skipTest("Failed to upload file for integration test")
        
        upload_data = response3.json()
        integration_file_id = upload_data['file_id']
        
        # Step 4: Retrieve file list
        success4, response4 = self.tester.run_test(
            "Integration - Get Files",
            "GET",
            "user/files",
            200,
            auth=True
        )
        self.assertTrue(success4)
        
        # Step 5: Retrieve specific file data
        success5, response5 = self.tester.run_test(
            "Integration - Get File Data",
            "GET",
            f"user/data/{integration_file_id}",
            200,
            auth=True
        )
        self.assertTrue(success5)
        
        # Step 6: Chat with user data
        success6, response6 = self.tester.run_test(
            "Integration - Chat With User Data",
            "POST",
            "chat",
            200,
            data={
                "query": "Analyze my uploaded data",
                "user_id": integration_user_id
            }
        )
        self.assertTrue(success6)
        
        # Verify user data is included in chat results
        if success6:
            chat_data = response6.json()
            user_data_found = False
            for result in chat_data['results']:
                if 'is_user_data' in result and result['is_user_data']:
                    user_data_found = True
            
            self.assertTrue(user_data_found, "User data should be included in chat results")
        
        # Step 7: Logout
        success7, response7 = self.tester.run_test(
            "Integration - Logout",
            "POST",
            "logout",
            200,
            auth=True
        )
        self.assertTrue(success7)
        
        print("\n✅ Full integration flow completed successfully!")

    @classmethod
    def tearDownClass(cls):
        cls.tester.print_summary()

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)