import requests
import unittest
import sys
import json
import os
import csv
import io
from datetime import datetime

class TRACITYAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.auth_token = None
        self.user_id = None

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

class TestTRACITYAuthAndFileUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get the backend URL from the environment variable
        cls.base_url = "https://38c5b002-937f-4add-9333-a54cc7abea8a.preview.emergentagent.com/api"
        cls.tester = TRACITYAPITester(cls.base_url)
        print(f"Testing API at: {cls.base_url}")
        
        # Test user credentials
        cls.test_user = {
            "email": f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            "password": "SecurePassword123!"
        }
        
        # Create test files
        cls.create_test_files()

    @classmethod
    def create_test_files(cls):
        """Create test CSV and JSON files for upload testing"""
        # Create a test CSV file
        cls.csv_data = [
            ["name", "age", "city"],
            ["John Doe", 30, "Mumbai"],
            ["Jane Smith", 25, "Delhi"],
            ["Bob Johnson", 40, "Bangalore"]
        ]
        
        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        for row in cls.csv_data:
            writer.writerow(row)
        cls.csv_content = csv_file.getvalue()
        
        # Create a test JSON file
        cls.json_data = [
            {"name": "John Doe", "age": 30, "city": "Mumbai"},
            {"name": "Jane Smith", "age": 25, "city": "Delhi"},
            {"name": "Bob Johnson", "age": 40, "city": "Bangalore"}
        ]
        cls.json_content = json.dumps(cls.json_data)

    def test_01_captcha_endpoint(self):
        """Test the captcha endpoint generates math captcha properly"""
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
            
            # Verify the question is a math captcha
            self.assertIn("What is", data["question"])
            self.assertIn("+", data["question"])
            
            # Store session_id for login test
            self.session_id = data["session_id"]
            
            # Extract the answer from the question
            question = data["question"]
            numbers = [int(s) for s in question.split() if s.isdigit()]
            self.captcha_answer = sum(numbers)
            
            print(f"Captcha Question: {question}")
            print(f"Captcha Answer: {self.captcha_answer}")

    def test_02_login_with_valid_credentials(self):
        """Test login endpoint with valid credentials"""
        # Make sure captcha test ran first
        if not hasattr(self, 'captcha_answer'):
            self.test_01_captcha_endpoint()
        
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"],
            "captcha_answer": self.captcha_answer
        }
        
        success, response = self.tester.run_test(
            "Login with Valid Credentials",
            "POST",
            "login",
            200,
            data=login_data
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("token", data)
            self.assertIn("user_id", data)
            self.assertIn("email", data)
            self.assertIn("message", data)
            
            # Store token and user_id for subsequent tests
            self.tester.auth_token = data["token"]
            self.tester.user_id = data["user_id"]
            
            print(f"Login successful - User ID: {data['user_id']}")
            print(f"Message: {data['message']}")

    def test_03_login_with_invalid_captcha(self):
        """Test login with invalid captcha fails appropriately"""
        # Get a new captcha
        success, response = self.tester.run_test(
            "Get New Captcha for Invalid Test",
            "GET",
            "captcha",
            200
        )
        self.assertTrue(success)
        
        if success:
            # Use an incorrect captcha answer
            login_data = {
                "email": self.test_user["email"],
                "password": self.test_user["password"],
                "captcha_answer": 9999  # Incorrect answer
            }
            
            success, response = self.tester.run_test(
                "Login with Invalid Captcha",
                "POST",
                "login",
                401,  # Expecting unauthorized
                data=login_data
            )
            
            # This test is successful if the login fails with 401
            self.assertTrue(success)
            if success and response:
                data = response.json()
                self.assertIn("detail", data)
                print(f"Invalid captcha error: {data['detail']}")

    def test_04_token_validation(self):
        """Test token validation works for authenticated endpoints"""
        # Make sure login test ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        
        # Test an authenticated endpoint
        success, response = self.tester.run_test(
            "Token Validation",
            "GET",
            "user/files",
            200
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("user_id", data)
            self.assertIn("files", data)
            self.assertIn("total_files", data)
            
            # Verify the user_id matches
            self.assertEqual(data["user_id"], self.tester.user_id)
            
            print(f"Token validation successful - User ID: {data['user_id']}")
            print(f"Total files: {data['total_files']}")

    def test_05_token_validation_with_invalid_token(self):
        """Test token validation fails with invalid token"""
        # Use an invalid token
        invalid_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer InvalidToken123'
        }
        
        success, response = self.tester.run_test(
            "Token Validation with Invalid Token",
            "GET",
            "user/files",
            401,  # Expecting unauthorized
            headers=invalid_headers
        )
        
        # This test is successful if the request fails with 401
        self.assertTrue(success)
        if success and response:
            data = response.json()
            self.assertIn("detail", data)
            print(f"Invalid token error: {data['detail']}")

    def test_06_upload_csv_file(self):
        """Test upload endpoint with CSV file upload"""
        # Make sure login test ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        
        # Prepare the file for upload
        files = {
            'file': ('test_data.csv', self.csv_content, 'text/csv')
        }
        
        success, response = self.tester.run_test(
            "Upload CSV File",
            "POST",
            "upload",
            200,
            files=files
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("file_id", data)
            self.assertIn("filename", data)
            self.assertIn("record_count", data)
            self.assertIn("message", data)
            
            # Store file_id for subsequent tests
            self.csv_file_id = data["file_id"]
            
            # Verify record count matches our test data
            self.assertEqual(data["record_count"], len(self.csv_data) - 1)  # Subtract 1 for header row
            
            print(f"CSV upload successful - File ID: {data['file_id']}")
            print(f"Record count: {data['record_count']}")
            print(f"Message: {data['message']}")

    def test_07_upload_json_file(self):
        """Test upload endpoint with JSON file upload"""
        # Make sure login test ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        
        # Prepare the file for upload
        files = {
            'file': ('test_data.json', self.json_content, 'application/json')
        }
        
        success, response = self.tester.run_test(
            "Upload JSON File",
            "POST",
            "upload",
            200,
            files=files
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("file_id", data)
            self.assertIn("filename", data)
            self.assertIn("record_count", data)
            self.assertIn("message", data)
            
            # Store file_id for subsequent tests
            self.json_file_id = data["file_id"]
            
            # Verify record count matches our test data
            self.assertEqual(data["record_count"], len(self.json_data))
            
            print(f"JSON upload successful - File ID: {data['file_id']}")
            print(f"Record count: {data['record_count']}")
            print(f"Message: {data['message']}")

    def test_08_upload_without_authentication(self):
        """Test file upload without authentication fails"""
        # Prepare the file for upload
        files = {
            'file': ('test_data.csv', self.csv_content, 'text/csv')
        }
        
        # Use a request without authentication
        headers = {'Content-Type': 'multipart/form-data'}
        
        success, response = self.tester.run_test(
            "Upload Without Authentication",
            "POST",
            "upload",
            401,  # Expecting unauthorized
            files=files,
            headers=headers
        )
        
        # This test is successful if the upload fails with 401
        self.assertTrue(success)
        if success and response:
            data = response.json()
            self.assertIn("detail", data)
            print(f"Unauthenticated upload error: {data['detail']}")

    def test_09_user_files_list(self):
        """Test user/files endpoint returns user's uploaded files list"""
        # Make sure login and upload tests ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        if not hasattr(self, 'csv_file_id') or not hasattr(self, 'json_file_id'):
            self.test_06_upload_csv_file()
            self.test_07_upload_json_file()
        
        success, response = self.tester.run_test(
            "Get User Files List",
            "GET",
            "user/files",
            200
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("user_id", data)
            self.assertIn("files", data)
            self.assertIn("total_files", data)
            
            # Verify the user_id matches
            self.assertEqual(data["user_id"], self.tester.user_id)
            
            # Verify we have at least 2 files (CSV and JSON)
            self.assertGreaterEqual(data["total_files"], 2)
            
            # Verify our uploaded files are in the list
            file_ids = [file["file_id"] for file in data["files"]]
            self.assertIn(self.csv_file_id, file_ids)
            self.assertIn(self.json_file_id, file_ids)
            
            print(f"User files list - Total files: {data['total_files']}")
            for file in data["files"]:
                print(f"- {file['filename']} ({file['file_type']}) - {file['record_count']} records")

    def test_10_user_file_data(self):
        """Test user/data/{file_id} endpoint retrieves specific user file data"""
        # Make sure login and upload tests ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        if not hasattr(self, 'csv_file_id'):
            self.test_06_upload_csv_file()
        
        success, response = self.tester.run_test(
            "Get User File Data",
            "GET",
            f"user/data/{self.csv_file_id}",
            200
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("file_id", data)
            self.assertIn("filename", data)
            self.assertIn("data", data)
            self.assertIn("record_count", data)
            
            # Verify the file_id matches
            self.assertEqual(data["file_id"], self.csv_file_id)
            
            # Verify record count matches our test data
            self.assertEqual(data["record_count"], len(self.csv_data) - 1)  # Subtract 1 for header row
            
            # Verify the data structure matches our test data
            self.assertEqual(len(data["data"]), len(self.csv_data) - 1)
            
            print(f"User file data - File ID: {data['file_id']}")
            print(f"Record count: {data['record_count']}")
            print(f"Sample data: {data['data'][0]}")

    def test_11_user_file_data_with_invalid_file_id(self):
        """Test user/data/{file_id} endpoint with invalid file_id"""
        # Make sure login test ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        
        invalid_file_id = "invalid_file_id_123"
        
        success, response = self.tester.run_test(
            "Get User File Data with Invalid File ID",
            "GET",
            f"user/data/{invalid_file_id}",
            404,  # Expecting not found
        )
        
        # This test is successful if the request fails with 404
        self.assertTrue(success)
        if success and response:
            data = response.json()
            self.assertIn("detail", data)
            print(f"Invalid file ID error: {data['detail']}")

    def test_12_user_collection_creation(self):
        """Test file processing creates user-specific collection"""
        # Make sure login and upload tests ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        if not hasattr(self, 'csv_file_id'):
            self.test_06_upload_csv_file()
        
        # Get user files to check collection name
        success, response = self.tester.run_test(
            "Get User Files for Collection Check",
            "GET",
            "user/files",
            200
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            
            # Find our CSV file
            csv_file = None
            for file in data["files"]:
                if file["file_id"] == self.csv_file_id:
                    csv_file = file
                    break
            
            self.assertIsNotNone(csv_file)
            self.assertIn("collection_name", csv_file)
            
            # Verify collection name follows the expected format
            expected_collection_name = f"user_{self.tester.user_id}_files"
            self.assertEqual(csv_file["collection_name"], expected_collection_name)
            
            print(f"User collection name: {csv_file['collection_name']}")

    def test_13_file_metadata_storage(self):
        """Test file metadata is stored in user_files collection"""
        # Make sure login and upload tests ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        if not hasattr(self, 'csv_file_id'):
            self.test_06_upload_csv_file()
        
        # Get user files to check metadata
        success, response = self.tester.run_test(
            "Get User Files for Metadata Check",
            "GET",
            "user/files",
            200
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            
            # Find our CSV file
            csv_file = None
            for file in data["files"]:
                if file["file_id"] == self.csv_file_id:
                    csv_file = file
                    break
            
            self.assertIsNotNone(csv_file)
            
            # Verify metadata fields
            self.assertIn("file_id", csv_file)
            self.assertIn("filename", csv_file)
            self.assertIn("user_id", csv_file)
            self.assertIn("upload_date", csv_file)
            self.assertIn("record_count", csv_file)
            self.assertIn("file_type", csv_file)
            self.assertIn("collection_name", csv_file)
            
            # Verify values
            self.assertEqual(csv_file["file_id"], self.csv_file_id)
            self.assertEqual(csv_file["user_id"], self.tester.user_id)
            self.assertEqual(csv_file["file_type"], "csv")
            self.assertEqual(csv_file["record_count"], len(self.csv_data) - 1)  # Subtract 1 for header row
            
            print(f"File metadata - File ID: {csv_file['file_id']}")
            print(f"Upload date: {csv_file['upload_date']}")
            print(f"File type: {csv_file['file_type']}")
            print(f"Record count: {csv_file['record_count']}")

    def test_14_enhanced_chat_with_user_data(self):
        """Test enhanced chat includes user data when user_id is provided"""
        # Make sure login and upload tests ran first
        if not self.tester.auth_token:
            self.test_02_login_with_valid_credentials()
        if not hasattr(self, 'csv_file_id'):
            self.test_06_upload_csv_file()
        
        # Test chat with user_id
        chat_data = {
            "query": "Show me my uploaded data",
            "user_id": self.tester.user_id
        }
        
        success, response = self.tester.run_test(
            "Enhanced Chat with User Data",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("query", data)
            self.assertIn("results", data)
            
            # Check if any result mentions user data
            user_data_found = False
            for result in data["results"]:
                if "is_user_data" in result and result["is_user_data"]:
                    user_data_found = True
                    break
                
                # Also check for mentions of "your data" in insights
                if "insight" in result and ("your data" in result["insight"].lower() or "your file" in result["insight"].lower()):
                    user_data_found = True
                    break
            
            self.assertTrue(user_data_found, "Chat response should include user data")
            
            print(f"Chat with user data - Results: {len(data['results'])}")
            for result in data["results"]:
                if "is_user_data" in result and result["is_user_data"]:
                    print(f"- User data found: {result['collection']}")
                    print(f"- Insight: {result['insight'][:100]}...")

    def test_15_datasets_exclude_system_collections(self):
        """Test datasets endpoint excludes system collections"""
        success, response = self.tester.run_test(
            "Datasets Endpoint",
            "GET",
            "datasets",
            200
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            
            # Check that system collections are excluded
            collection_names = [dataset["collection"] for dataset in data]
            
            # System collections that should be excluded
            system_collections = ["users", "user_files", "user_profiles"]
            
            for system_collection in system_collections:
                self.assertNotIn(system_collection, collection_names, 
                                f"System collection '{system_collection}' should be excluded")
            
            # Check that user-specific collections are excluded
            user_collection_prefix = "user_"
            for collection in collection_names:
                self.assertFalse(collection.startswith(user_collection_prefix), 
                                f"User collection '{collection}' should be excluded")
            
            print(f"Datasets endpoint - Collections: {collection_names}")

    def test_16_complete_flow(self):
        """Test the complete authentication and file upload flow"""
        # 1. Get captcha
        success, captcha_response = self.tester.run_test(
            "Complete Flow - Get Captcha",
            "GET",
            "captcha",
            200
        )
        self.assertTrue(success)
        
        if not success:
            return
            
        captcha_data = captcha_response.json()
        question = captcha_data["question"]
        numbers = [int(s) for s in question.split() if s.isdigit()]
        captcha_answer = sum(numbers)
        
        # 2. Login with captcha
        login_data = {
            "email": f"complete_flow_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            "password": "CompleteFlowTest123!",
            "captcha_answer": captcha_answer
        }
        
        success, login_response = self.tester.run_test(
            "Complete Flow - Login",
            "POST",
            "login",
            200,
            data=login_data
        )
        self.assertTrue(success)
        
        if not success:
            return
            
        login_data = login_response.json()
        token = login_data["token"]
        user_id = login_data["user_id"]
        
        # Set auth token for subsequent requests
        auth_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {token}"
        }
        
        # 3. Upload CSV file
        files = {
            'file': ('complete_flow.csv', self.csv_content, 'text/csv')
        }
        
        success, upload_response = self.tester.run_test(
            "Complete Flow - Upload CSV",
            "POST",
            "upload",
            200,
            files=files,
            headers={'Authorization': f"Bearer {token}"}
        )
        self.assertTrue(success)
        
        if not success:
            return
            
        upload_data = upload_response.json()
        file_id = upload_data["file_id"]
        
        # 4. Get user files list
        success, files_response = self.tester.run_test(
            "Complete Flow - Get Files List",
            "GET",
            "user/files",
            200,
            headers=auth_headers
        )
        self.assertTrue(success)
        
        if not success:
            return
            
        files_data = files_response.json()
        self.assertEqual(files_data["user_id"], user_id)
        self.assertGreaterEqual(files_data["total_files"], 1)
        
        # 5. Get specific file data
        success, file_data_response = self.tester.run_test(
            "Complete Flow - Get File Data",
            "GET",
            f"user/data/{file_id}",
            200,
            headers=auth_headers
        )
        self.assertTrue(success)
        
        if not success:
            return
            
        file_data = file_data_response.json()
        self.assertEqual(file_data["file_id"], file_id)
        
        # 6. Chat with user data
        chat_data = {
            "query": "Show me my uploaded data",
            "user_id": user_id
        }
        
        success, chat_response = self.tester.run_test(
            "Complete Flow - Chat with User Data",
            "POST",
            "chat",
            200,
            data=chat_data,
            headers=auth_headers
        )
        self.assertTrue(success)
        
        if success:
            chat_data = chat_response.json()
            
            # Check if any result mentions user data
            user_data_found = False
            for result in chat_data["results"]:
                if "is_user_data" in result and result["is_user_data"]:
                    user_data_found = True
                    break
                
                # Also check for mentions of "your data" in insights
                if "insight" in result and ("your data" in result["insight"].lower() or "your file" in result["insight"].lower()):
                    user_data_found = True
                    break
            
            self.assertTrue(user_data_found, "Chat response should include user data")
            
            print("\n✅ Complete authentication and file upload flow test passed!")
            print("All steps completed successfully:")
            print("1. Generated captcha")
            print("2. Registered/logged in user")
            print("3. Uploaded CSV file")
            print("4. Retrieved user files list")
            print("5. Retrieved specific file data")
            print("6. Chat included user data")

    @classmethod
    def tearDownClass(cls):
        cls.tester.print_summary()

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)