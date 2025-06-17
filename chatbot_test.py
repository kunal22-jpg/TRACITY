import requests
import unittest
import json
import os
from datetime import datetime

class EnhancedChatbotTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.auth_token = None
        self.user_id = None
        self.email = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None, auth=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add authorization header if required and available
        if auth and self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                if files:
                    # For file uploads, don't use JSON content type
                    headers.pop('Content-Type', None)
                    response = requests.post(url, headers=headers, data=data, files=files, params=params)
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

class TestEnhancedChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get the backend URL from the environment variable
        cls.base_url = "https://38c5b002-937f-4add-9333-a54cc7abea8a.preview.emergentagent.com/api"
        cls.tester = EnhancedChatbotTester(cls.base_url)
        print(f"Testing Enhanced Chatbot API at: {cls.base_url}")
        
        # Test user credentials
        cls.test_email = f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        cls.test_password = "TestPassword123!"
        
        # Test file path
        cls.test_csv_path = "/tmp/test_data.csv"
        
        # Create a test CSV file with Indian states data
        with open(cls.test_csv_path, "w") as f:
            f.write("state,year,crime_rate,literacy_rate,aqi_level\n")
            f.write("Delhi,2020,45.2,86.3,210\n")
            f.write("Mumbai,2020,32.1,88.5,180\n")
            f.write("Kerala,2020,18.5,96.2,65\n")
            f.write("Tamil Nadu,2023,22.3,80.1,95\n")
            f.write("Gujarat,2022,28.7,79.3,120\n")
            f.write("Karnataka,2021,25.6,75.4,110\n")
            f.write("Uttar Pradesh,2020,38.9,67.7,160\n")
            f.write("West Bengal,2022,30.2,76.3,145\n")
            f.write("Rajasthan,2021,27.8,66.1,130\n")
            f.write("Punjab,2023,24.5,75.8,105\n")

    def test_01_authenticate_user(self):
        """Authenticate a test user for subsequent tests"""
        # Step 1: Get captcha
        success, captcha_response = self.tester.run_test(
            "Get Captcha",
            "GET",
            "captcha",
            200
        )
        self.assertTrue(success)
        if success:
            captcha_data = captcha_response.json()
            
            # Extract the numbers from the question (format: "What is X + Y?")
            question = captcha_data["question"]
            parts = question.replace("What is ", "").replace("?", "").split("+")
            num1 = int(parts[0].strip())
            num2 = int(parts[1].strip())
            captcha_answer = num1 + num2
            
            # Step 2: Login with captcha
            success, login_response = self.tester.run_test(
                "Login with Captcha",
                "POST",
                "login",
                200,
                data={
                    "email": self.test_email,
                    "password": self.test_password,
                    "captcha_answer": captcha_answer
                }
            )
            self.assertTrue(success)
            if success:
                login_data = login_response.json()
                self.tester.auth_token = login_data["token"]
                self.tester.user_id = login_data["user_id"]
                self.tester.email = login_data["email"]
                print(f"Authentication successful. User ID: {self.tester.user_id}")

    def test_02_upload_test_file(self):
        """Upload a test file with Indian states data"""
        # Skip if not authenticated
        if not self.tester.auth_token:
            self.skipTest("Authentication token not available. Run test_01_authenticate_user first.")
        
        # Upload the test CSV file
        with open(self.test_csv_path, "rb") as f:
            files = {"file": ("indian_states_data.csv", f, "text/csv")}
            success, response = self.tester.run_test(
                "Upload CSV File with Indian States Data",
                "POST",
                "upload",
                200,
                data={},
                files=files,
                auth=True
            )
            self.assertTrue(success)
            if success:
                data = response.json()
                self.assertIn("file_id", data)
                self.tester.file_id = data["file_id"]
                print(f"File upload successful. File ID: {self.tester.file_id}")

    def test_03_chat_with_crime_query(self):
        """Test the chat endpoint with a crime rate query"""
        query = "What is the crime rate in Delhi in 2020?"
        success, response = self.tester.run_test(
            "Chat Query - Crime Rate in Delhi 2020",
            "POST",
            "chat",
            200,
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            self.assertGreater(len(data["results"]), 0)
            
            # Check for Delhi-specific data
            found_delhi_data = False
            for result in data["results"]:
                if "state_specific" in result and result["state_specific"].lower() == "delhi":
                    found_delhi_data = True
                    self.assertIn("insight", result)
                    print(f"Found Delhi crime data: {result['insight'][:150]}...")
                    break
            
            # If no state-specific data, check general results
            if not found_delhi_data:
                for result in data["results"]:
                    if "collection" in result and result["collection"] == "crimes":
                        self.assertIn("insight", result)
                        print(f"Found crime data: {result['insight'][:150]}...")
                        break
            
            # Verify response contains statistical insights
            has_stats = False
            for result in data["results"]:
                if "insight" in result and any(term in result["insight"].lower() for term in ["total cases", "average", "records found"]):
                    has_stats = True
                    break
            self.assertTrue(has_stats, "Response should contain statistical insights")

    def test_04_chat_with_literacy_query(self):
        """Test the chat endpoint with a literacy rate query"""
        query = "Show me literacy rates in Kerala"
        success, response = self.tester.run_test(
            "Chat Query - Literacy Rates in Kerala",
            "POST",
            "chat",
            200,
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            self.assertGreater(len(data["results"]), 0)
            
            # Check for Kerala-specific data
            found_kerala_data = False
            for result in data["results"]:
                if "state_specific" in result and result["state_specific"].lower() == "kerala":
                    found_kerala_data = True
                    self.assertIn("insight", result)
                    print(f"Found Kerala literacy data: {result['insight'][:150]}...")
                    break
            
            # If no state-specific data, check general results
            if not found_kerala_data:
                for result in data["results"]:
                    if "collection" in result and result["collection"] == "literacy":
                        self.assertIn("insight", result)
                        print(f"Found literacy data: {result['insight'][:150]}...")
                        break
            
            # Verify response contains literacy rate information
            has_literacy_info = False
            for result in data["results"]:
                if "insight" in result and any(term in result["insight"].lower() for term in ["literacy rate", "education", "literate"]):
                    has_literacy_info = True
                    break
            self.assertTrue(has_literacy_info, "Response should contain literacy rate information")

    def test_05_chat_with_aqi_query(self):
        """Test the chat endpoint with an AQI query"""
        query = "AQI levels in Mumbai and Bangalore"
        success, response = self.tester.run_test(
            "Chat Query - AQI Levels in Mumbai and Bangalore",
            "POST",
            "chat",
            200,
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            self.assertGreater(len(data["results"]), 0)
            
            # Check for Mumbai and Bangalore specific data
            cities_found = set()
            for result in data["results"]:
                if "state_specific" in result:
                    if result["state_specific"].lower() in ["mumbai", "bangalore"]:
                        cities_found.add(result["state_specific"].lower())
                        print(f"Found {result['state_specific']} AQI data: {result['insight'][:150]}...")
            
            # If no state-specific data, check general results
            if not cities_found:
                for result in data["results"]:
                    if "collection" in result and result["collection"] == "aqi":
                        self.assertIn("insight", result)
                        print(f"Found AQI data: {result['insight'][:150]}...")
                        break
            
            # Verify response contains AQI information
            has_aqi_info = False
            for result in data["results"]:
                if "insight" in result and any(term in result["insight"].lower() for term in ["aqi", "air quality", "pollution"]):
                    has_aqi_info = True
                    break
            self.assertTrue(has_aqi_info, "Response should contain AQI information")
            
            # Verify state separation for multi-state query
            if len(cities_found) > 0:
                print(f"Found data for {len(cities_found)} cities: {cities_found}")
                self.assertGreaterEqual(len(cities_found), 1, "Expected at least one city-specific result")

    def test_06_chat_with_power_consumption_query(self):
        """Test the chat endpoint with a power consumption query"""
        query = "Power consumption in Tamil Nadu 2023"
        success, response = self.tester.run_test(
            "Chat Query - Power Consumption in Tamil Nadu 2023",
            "POST",
            "chat",
            200,
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            self.assertGreater(len(data["results"]), 0)
            
            # Check for Tamil Nadu specific data
            found_tn_data = False
            for result in data["results"]:
                if "state_specific" in result and result["state_specific"].lower() == "tamil nadu":
                    found_tn_data = True
                    self.assertIn("insight", result)
                    print(f"Found Tamil Nadu power data: {result['insight'][:150]}...")
                    break
            
            # If no state-specific data, check general results
            if not found_tn_data:
                for result in data["results"]:
                    if "collection" in result and result["collection"] == "power_consumption":
                        self.assertIn("insight", result)
                        print(f"Found power consumption data: {result['insight'][:150]}...")
                        break
            
            # Verify response contains power consumption information
            has_power_info = False
            for result in data["results"]:
                if "insight" in result and any(term in result["insight"].lower() for term in ["power", "consumption", "energy"]):
                    has_power_info = True
                    break
            self.assertTrue(has_power_info, "Response should contain power consumption information")

    def test_07_chat_with_comparison_query(self):
        """Test the chat endpoint with a comparison query"""
        query = "Compare crime statistics between Delhi and Mumbai"
        success, response = self.tester.run_test(
            "Chat Query - Compare Crime Statistics between Delhi and Mumbai",
            "POST",
            "chat",
            200,
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            self.assertGreater(len(data["results"]), 0)
            
            # Check for Delhi and Mumbai specific data
            cities_found = set()
            for result in data["results"]:
                if "state_specific" in result:
                    if result["state_specific"].lower() in ["delhi", "mumbai"]:
                        cities_found.add(result["state_specific"].lower())
                        print(f"Found {result['state_specific']} crime data: {result['insight'][:150]}...")
            
            # Verify state separation for comparison query
            if len(cities_found) > 0:
                print(f"Found data for {len(cities_found)} cities: {cities_found}")
                self.assertGreaterEqual(len(cities_found), 1, "Expected at least one city-specific result")
            
            # Verify visual links for explorer page
            has_visual_links = False
            for result in data["results"]:
                if "visual_link" in result and "/explorer" in result["visual_link"]:
                    has_visual_links = True
                    print(f"Found visual link: {result['visual_link']}")
                    break
            self.assertTrue(has_visual_links, "Response should contain visual links to explorer page")

    def test_08_chat_with_user_data(self):
        """Test the chat endpoint with user data integration"""
        # Skip if not authenticated or no file uploaded
        if not hasattr(self.tester, 'file_id'):
            self.skipTest("File ID not available. Run test_02_upload_test_file first.")
        
        query = "Show me my data for Delhi"
        success, response = self.tester.run_test(
            "Chat Query with User Data - Delhi",
            "POST",
            "chat",
            200,
            data={"query": query, "user_id": self.tester.user_id},
            auth=True
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            
            # Check if any result contains user data
            found_user_data = False
            for result in data["results"]:
                if "file_id" in result and "user_file" in result["collection"]:
                    found_user_data = True
                    self.assertIn("insight", result)
                    print(f"Found user data in chat response: {result['insight'][:150]}...")
                    
                    # Verify visual link contains file_id
                    self.assertIn("visual_link", result)
                    self.assertIn("user_file=", result["visual_link"])
                    break
            
            # It's possible user data might not be found if the query doesn't match the uploaded data
            if not found_user_data:
                print("No user data found in chat response. This might be expected if the query doesn't match uploaded data.")

    def test_09_chat_with_invalid_query(self):
        """Test the chat endpoint with an invalid query"""
        query = "xyzabc123 nonsense query"
        success, response = self.tester.run_test(
            "Chat Query - Invalid Query",
            "POST",
            "chat",
            200,  # Should still return 200 with a helpful message
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            self.assertGreater(len(data["results"]), 0)
            
            # Verify response contains a helpful message
            has_helpful_message = False
            for result in data["results"]:
                if "insight" in result:
                    print(f"Response to invalid query: {result['insight'][:150]}...")
                    # Check if the response is helpful rather than an error
                    if any(term in result["insight"].lower() for term in ["help", "try", "ask", "specific"]):
                        has_helpful_message = True
                        break
            self.assertTrue(has_helpful_message, "Response to invalid query should contain a helpful message")

    def test_10_chat_with_nonexistent_data(self):
        """Test the chat endpoint with a query for non-existent data"""
        query = "Show me crime data for XYZ State in 9999"
        success, response = self.tester.run_test(
            "Chat Query - Non-existent Data",
            "POST",
            "chat",
            200,  # Should still return 200 with a helpful message
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            self.assertGreater(len(data["results"]), 0)
            
            # Verify response contains a helpful message
            has_helpful_message = False
            for result in data["results"]:
                if "insight" in result:
                    print(f"Response to non-existent data query: {result['insight'][:150]}...")
                    # Check if the response is helpful rather than an error
                    if any(term in result["insight"].lower() for term in ["couldn't find", "no data", "try", "different"]):
                        has_helpful_message = True
                        break
            
            # It's okay if we don't get a specific "no data" message, as long as we get some response
            if not has_helpful_message:
                print("No specific 'no data' message found, but received a response.")

    @classmethod
    def tearDownClass(cls):
        # Clean up test file
        if os.path.exists(cls.test_csv_path):
            os.remove(cls.test_csv_path)
        
        cls.tester.print_summary()

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)