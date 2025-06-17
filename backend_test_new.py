import requests
import unittest
import sys
import json
from datetime import datetime
import random
import string

class TRACITYAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.token = None
        self.user_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if not headers:
            headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
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

class TestTRACITYNewFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get the backend URL from the environment variable
        cls.base_url = "https://38c5b002-937f-4add-9333-a54cc7abea8a.preview.emergentagent.com/api"
        cls.tester = TRACITYAPITester(cls.base_url)
        print(f"Testing API at: {cls.base_url}")
        
        # Generate random user credentials for testing
        cls.test_email = f"test_{random.randint(1000, 9999)}@example.com"
        cls.test_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        print(f"Using test credentials: {cls.test_email} / {cls.test_password}")

    def test_01_login_flow(self):
        """Test the login flow and verify authentication"""
        # Step 1: Get captcha
        success, response = self.tester.run_test(
            "Get Captcha",
            "GET",
            "captcha",
            200
        )
        self.assertTrue(success)
        
        if success:
            captcha_data = response.json()
            self.assertIn("question", captcha_data)
            self.assertIn("session_id", captcha_data)
            
            # Extract the numbers from the question (format: "What is X + Y?")
            question = captcha_data["question"]
            print(f"Captcha question: {question}")
            
            # Parse the question to get the answer
            parts = question.split()
            num1 = int(parts[2])
            num2 = int(parts[4].replace("?", ""))
            captcha_answer = num1 + num2
            print(f"Calculated captcha answer: {captcha_answer}")
            
            # Step 2: Login with the captcha
            login_data = {
                "email": self.test_email,
                "password": self.test_password,
                "captcha_answer": captcha_answer
            }
            
            success, response = self.tester.run_test(
                "Login User",
                "POST",
                "login",
                200,
                data=login_data
            )
            self.assertTrue(success)
            
            if success:
                login_response = response.json()
                self.assertIn("token", login_response)
                self.assertIn("user_id", login_response)
                self.assertIn("email", login_response)
                self.assertIn("message", login_response)
                
                # Store token and user_id for subsequent tests
                self.tester.token = login_response["token"]
                self.tester.user_id = login_response["user_id"]
                
                print(f"Successfully logged in. User ID: {self.tester.user_id}")
                print(f"Login message: {login_response['message']}")
                
                # Verify the token works by accessing a protected endpoint
                auth_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.tester.token}'
                }
                
                success, response = self.tester.run_test(
                    "Verify Authentication",
                    "GET",
                    "user/files",
                    200,
                    headers=auth_headers
                )
                self.assertTrue(success)
                
                if success:
                    files_data = response.json()
                    self.assertIn("user_id", files_data)
                    self.assertIn("files", files_data)
                    self.assertIn("total_files", files_data)
                    print(f"Authentication verified. User has {files_data['total_files']} files.")

    def test_02_file_upload(self):
        """Test the file upload functionality"""
        if not self.tester.token:
            self.skipTest("Authentication token not available. Login test must pass first.")
        
        # Create a simple CSV file for testing
        csv_content = "state,year,value\nDelhi,2022,100\nMumbai,2022,150\nBangalore,2022,120"
        
        # Set up headers with authentication token
        auth_headers = {
            'Authorization': f'Bearer {self.tester.token}'
        }
        
        # Create a file-like object
        files = {
            'file': ('test_data.csv', csv_content, 'text/csv')
        }
        
        # Make the request directly using requests library since our tester doesn't handle file uploads
        print("\n🔍 Testing File Upload...")
        try:
            response = requests.post(
                f"{self.tester.base_url}/upload",
                headers=auth_headers,
                files=files
            )
            
            success = response.status_code == 200
            
            if success:
                self.tester.tests_run += 1
                self.tester.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                upload_response = response.json()
                self.assertIn("file_id", upload_response)
                self.assertIn("filename", upload_response)
                self.assertIn("record_count", upload_response)
                self.assertIn("message", upload_response)
                
                # Store the file_id for subsequent tests
                self.file_id = upload_response["file_id"]
                
                print(f"File uploaded successfully. File ID: {self.file_id}")
                print(f"Record count: {upload_response['record_count']}")
                print(f"Message: {upload_response['message']}")
                
                # Verify the file appears in the user's files list
                success, response = self.tester.run_test(
                    "Verify File in User Files",
                    "GET",
                    "user/files",
                    200,
                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.tester.token}'}
                )
                self.assertTrue(success)
                
                if success:
                    files_data = response.json()
                    self.assertIn("files", files_data)
                    self.assertGreater(len(files_data["files"]), 0)
                    
                    # Check if our uploaded file is in the list
                    file_found = False
                    for file in files_data["files"]:
                        if file["file_id"] == self.file_id:
                            file_found = True
                            break
                    
                    self.assertTrue(file_found, "Uploaded file not found in user's files list")
                    print("Uploaded file found in user's files list.")
            else:
                self.tester.tests_run += 1
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error = response.json()
                    print(f"Error: {error}")
                except:
                    print(f"Error: {response.text}")
                
                self.fail(f"File upload failed with status code {response.status_code}")
                
        except Exception as e:
            self.tester.tests_run += 1
            print(f"❌ Failed - Error: {str(e)}")
            self.fail(f"File upload test failed with error: {str(e)}")

    def test_03_user_file_data(self):
        """Test retrieving data from an uploaded file"""
        if not hasattr(self, 'file_id'):
            self.skipTest("File ID not available. File upload test must pass first.")
        
        auth_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.tester.token}'
        }
        
        success, response = self.tester.run_test(
            "Get User File Data",
            "GET",
            f"user/data/{self.file_id}",
            200,
            headers=auth_headers
        )
        self.assertTrue(success)
        
        if success:
            file_data = response.json()
            self.assertIn("file_id", file_data)
            self.assertIn("filename", file_data)
            self.assertIn("data", file_data)
            self.assertIn("record_count", file_data)
            
            # Verify the data matches what we uploaded
            self.assertEqual(file_data["file_id"], self.file_id)
            self.assertEqual(file_data["record_count"], 3)  # We uploaded 3 records
            
            # Check the data content
            data = file_data["data"]
            self.assertEqual(len(data), 3)
            
            # Verify the data fields
            for record in data:
                self.assertIn("state", record)
                self.assertIn("year", record)
                self.assertIn("value", record)
            
            print(f"Successfully retrieved file data with {file_data['record_count']} records.")
            print(f"Sample data: {data[0]}")

    def test_04_enhanced_user_file_insights(self):
        """Test the new enhanced user file insights endpoint"""
        if not hasattr(self, 'file_id'):
            self.skipTest("File ID not available. File upload test must pass first.")
        
        auth_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.tester.token}'
        }
        
        # Test with different chart types
        chart_types = ["bar", "line", "pie", "doughnut"]
        
        for chart_type in chart_types:
            request_data = {
                "chart_type": chart_type,
                "filename": "test_data.csv",
                "record_count": 3
            }
            
            success, response = self.tester.run_test(
                f"Enhanced User File Insights - {chart_type} chart",
                "POST",
                f"user/insights/{self.file_id}",
                200,
                data=request_data,
                headers=auth_headers
            )
            self.assertTrue(success)
            
            if success:
                insights_data = response.json()
                self.assertIn("insights", insights_data)
                insights = insights_data["insights"]
                
                # Verify the insights structure
                self.assertIn("insight", insights)
                self.assertIn("chart_type", insights)
                self.assertIn("key_findings", insights)
                self.assertIn("recommendations", insights)
                self.assertIn("state_comparisons", insights)
                self.assertIn("temporal_analysis", insights)
                self.assertIn("anomaly_detection", insights)
                
                # Verify chart type is correctly set
                self.assertEqual(insights["chart_type"], chart_type)
                
                # Verify key findings and recommendations are present
                self.assertGreaterEqual(len(insights["key_findings"]), 3)
                self.assertGreaterEqual(len(insights["recommendations"]), 3)
                self.assertGreaterEqual(len(insights["state_comparisons"]), 2)
                self.assertGreaterEqual(len(insights["temporal_analysis"]), 2)
                self.assertGreaterEqual(len(insights["anomaly_detection"]), 2)
                
                print(f"Enhanced insights for {chart_type} chart:")
                print(f"- Insight: {insights['insight'][:100]}...")
                print(f"- Key findings: {len(insights['key_findings'])} items")
                print(f"- Recommendations: {len(insights['recommendations'])} items")
                print(f"- State comparisons: {len(insights['state_comparisons'])} items")
                print(f"- Temporal analysis: {len(insights['temporal_analysis'])} items")
                print(f"- Anomaly detection: {len(insights['anomaly_detection'])} items")

    def test_05_dataset_filtering_for_authenticated_users(self):
        """Test that authenticated users see both public datasets and their uploaded files"""
        if not self.tester.token:
            self.skipTest("Authentication token not available. Login test must pass first.")
        
        # First, test without authentication to see only public datasets
        success, response = self.tester.run_test(
            "Get Datasets - Unauthenticated",
            "GET",
            "datasets",
            200
        )
        self.assertTrue(success)
        
        if success:
            public_datasets = response.json()
            public_collections = [dataset["collection"] for dataset in public_datasets]
            
            print(f"Public datasets (unauthenticated): {public_collections}")
            
            # Verify only public datasets are shown (no user collections)
            for collection in public_collections:
                self.assertFalse(collection.startswith("user_"), f"User collection {collection} should not be visible to unauthenticated users")
                self.assertNotIn(collection, ["users", "user_files", "user_profiles"], f"System collection {collection} should not be visible")
            
            # Now test with authentication
            auth_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.tester.token}'
            }
            
            success, response = self.tester.run_test(
                "Get Datasets - Authenticated",
                "GET",
                "datasets",
                200,
                headers=auth_headers
            )
            self.assertTrue(success)
            
            if success:
                auth_datasets = response.json()
                auth_collections = [dataset["collection"] for dataset in auth_datasets]
                
                print(f"Datasets (authenticated): {auth_collections}")
                
                # Verify system collections are not shown
                for collection in auth_collections:
                    self.assertNotIn(collection, ["users", "user_files", "user_profiles"], f"System collection {collection} should not be visible")
                
                # Verify the same public datasets are shown
                for collection in public_collections:
                    self.assertIn(collection, auth_collections, f"Public collection {collection} should be visible to authenticated users")

    def test_06_authentication_security(self):
        """Test authentication security by attempting to access protected endpoints without authentication"""
        # Try to access user files without authentication
        success, response = self.tester.run_test(
            "Access User Files - No Auth",
            "GET",
            "user/files",
            401  # Expect 401 Unauthorized
        )
        self.assertTrue(success)
        
        # Try to access user file data without authentication
        if hasattr(self, 'file_id'):
            success, response = self.tester.run_test(
                "Access User File Data - No Auth",
                "GET",
                f"user/data/{self.file_id}",
                401  # Expect 401 Unauthorized
            )
            self.assertTrue(success)
        
        # Try to access user file insights without authentication
        if hasattr(self, 'file_id'):
            success, response = self.tester.run_test(
                "Access User File Insights - No Auth",
                "POST",
                f"user/insights/{self.file_id}",
                401,  # Expect 401 Unauthorized
                data={"chart_type": "bar"}
            )
            self.assertTrue(success)
        
        # Try to upload a file without authentication
        files = {
            'file': ('test_data.csv', "state,year,value\nTest,2022,100", 'text/csv')
        }
        
        print("\n🔍 Testing File Upload - No Auth...")
        try:
            response = requests.post(
                f"{self.tester.base_url}/upload",
                files=files
            )
            
            # Should get 401 Unauthorized
            success = response.status_code == 401
            
            if success:
                self.tester.tests_run += 1
                self.tester.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} (Expected 401)")
            else:
                self.tester.tests_run += 1
                print(f"❌ Failed - Expected 401, got {response.status_code}")
                try:
                    error = response.json()
                    print(f"Error: {error}")
                except:
                    print(f"Error: {response.text}")
                
                self.fail(f"File upload without authentication should fail with 401, got {response.status_code}")
                
        except Exception as e:
            self.tester.tests_run += 1
            print(f"❌ Failed - Error: {str(e)}")
            self.fail(f"File upload without authentication test failed with error: {str(e)}")

    def test_07_file_validation(self):
        """Test file validation by attempting to upload invalid file types"""
        if not self.tester.token:
            self.skipTest("Authentication token not available. Login test must pass first.")
        
        # Set up headers with authentication token
        auth_headers = {
            'Authorization': f'Bearer {self.tester.token}'
        }
        
        # Try to upload a text file (not CSV or JSON)
        files = {
            'file': ('test_data.txt', "This is a text file, not CSV or JSON", 'text/plain')
        }
        
        print("\n🔍 Testing File Validation - Invalid File Type...")
        try:
            response = requests.post(
                f"{self.tester.base_url}/upload",
                headers=auth_headers,
                files=files
            )
            
            # Should get 400 Bad Request
            success = response.status_code == 400
            
            if success:
                self.tester.tests_run += 1
                self.tester.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} (Expected 400)")
                try:
                    error = response.json()
                    print(f"Error message: {error['detail']}")
                    self.assertIn("Only CSV and JSON files are allowed", error['detail'])
                except:
                    print(f"Error: {response.text}")
            else:
                self.tester.tests_run += 1
                print(f"❌ Failed - Expected 400, got {response.status_code}")
                try:
                    error = response.json()
                    print(f"Error: {error}")
                except:
                    print(f"Error: {response.text}")
                
                self.fail(f"Invalid file type upload should fail with 400, got {response.status_code}")
                
        except Exception as e:
            self.tester.tests_run += 1
            print(f"❌ Failed - Error: {str(e)}")
            self.fail(f"File validation test failed with error: {str(e)}")

    def test_08_integration_test_full_flow(self):
        """Test the complete flow: login → upload → retrieve → insights"""
        # Step 1: Get captcha
        success, response = self.tester.run_test(
            "Integration Test - Get Captcha",
            "GET",
            "captcha",
            200
        )
        self.assertTrue(success)
        
        if success:
            captcha_data = response.json()
            
            # Parse the question to get the answer
            question = captcha_data["question"]
            parts = question.split()
            num1 = int(parts[2])
            num2 = int(parts[4].replace("?", ""))
            captcha_answer = num1 + num2
            
            # Step 2: Login with the captcha
            login_data = {
                "email": f"integration_{random.randint(1000, 9999)}@example.com",
                "password": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
                "captcha_answer": captcha_answer
            }
            
            success, response = self.tester.run_test(
                "Integration Test - Login",
                "POST",
                "login",
                200,
                data=login_data
            )
            self.assertTrue(success)
            
            if success:
                login_response = response.json()
                token = login_response["token"]
                user_id = login_response["user_id"]
                
                # Step 3: Upload a file
                auth_headers = {
                    'Authorization': f'Bearer {token}'
                }
                
                csv_content = "state,year,value\nDelhi,2022,100\nMumbai,2022,150\nBangalore,2022,120"
                files = {
                    'file': ('integration_test.csv', csv_content, 'text/csv')
                }
                
                print("\n🔍 Integration Test - Upload File...")
                try:
                    response = requests.post(
                        f"{self.tester.base_url}/upload",
                        headers=auth_headers,
                        files=files
                    )
                    
                    success = response.status_code == 200
                    
                    if success:
                        self.tester.tests_run += 1
                        self.tester.tests_passed += 1
                        print(f"✅ Passed - Status: {response.status_code}")
                        
                        upload_response = response.json()
                        file_id = upload_response["file_id"]
                        
                        # Step 4: Get user files
                        json_headers = {
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {token}'
                        }
                        
                        success, response = self.tester.run_test(
                            "Integration Test - Get User Files",
                            "GET",
                            "user/files",
                            200,
                            headers=json_headers
                        )
                        self.assertTrue(success)
                        
                        if success:
                            # Step 5: Get file data
                            success, response = self.tester.run_test(
                                "Integration Test - Get File Data",
                                "GET",
                                f"user/data/{file_id}",
                                200,
                                headers=json_headers
                            )
                            self.assertTrue(success)
                            
                            if success:
                                # Step 6: Get file insights
                                request_data = {
                                    "chart_type": "bar",
                                    "filename": "integration_test.csv",
                                    "record_count": 3
                                }
                                
                                success, response = self.tester.run_test(
                                    "Integration Test - Get File Insights",
                                    "POST",
                                    f"user/insights/{file_id}",
                                    200,
                                    data=request_data,
                                    headers=json_headers
                                )
                                self.assertTrue(success)
                                
                                if success:
                                    # Step 7: Test chat with user data
                                    chat_data = {
                                        "query": "Show me my data",
                                        "user_id": user_id
                                    }
                                    
                                    success, response = self.tester.run_test(
                                        "Integration Test - Chat with User Data",
                                        "POST",
                                        "chat",
                                        200,
                                        data=chat_data
                                    )
                                    self.assertTrue(success)
                                    
                                    if success:
                                        chat_response = response.json()
                                        self.assertIn("results", chat_response)
                                        
                                        # Check if any result mentions the user's data
                                        user_data_found = False
                                        for result in chat_response["results"]:
                                            if "is_user_data" in result and result["is_user_data"]:
                                                user_data_found = True
                                                break
                                            
                                            if "insight" in result and "your data" in result["insight"].lower():
                                                user_data_found = True
                                                break
                                        
                                        print(f"Chat with user data - User data found: {user_data_found}")
                    else:
                        self.tester.tests_run += 1
                        print(f"❌ Failed - Expected 200, got {response.status_code}")
                        try:
                            error = response.json()
                            print(f"Error: {error}")
                        except:
                            print(f"Error: {response.text}")
                        
                        self.fail(f"Integration test file upload failed with status code {response.status_code}")
                        
                except Exception as e:
                    self.tester.tests_run += 1
                    print(f"❌ Failed - Error: {str(e)}")
                    self.fail(f"Integration test file upload failed with error: {str(e)}")

    @classmethod
    def tearDownClass(cls):
        cls.tester.print_summary()

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)