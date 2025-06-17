import requests
import unittest
import sys
import json
import os
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
        self.email = None
        self.file_id = None

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
                        # Print a truncated version of the response for debugging
                        if name.startswith("Chat Query") or "Chat" in name:
                            print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
                    except:
                        result["response"] = response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    result["error"] = response.json()
                    print(f"Error: {json.dumps(response.json(), indent=2)}")
                except:
                    result["error"] = response.text
                    print(f"Error: {response.text}")
            
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

class TestTRACITYChatAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get the backend URL from the environment variable
        cls.base_url = "https://38c5b002-937f-4add-9333-a54cc7abea8a.preview.emergentagent.com/api"
        cls.tester = TRACITYAPITester(cls.base_url)
        print(f"Testing API at: {cls.base_url}")
        
        # Test user credentials
        cls.test_email = f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        cls.test_password = "TestPassword123!"
        
        # Test file path
        cls.test_csv_path = "/tmp/test_data.csv"
        
        # Create a test CSV file
        with open(cls.test_csv_path, "w") as f:
            f.write("state,year,value,category\n")
            f.write("Delhi,2020,100,Test\n")
            f.write("Mumbai,2020,200,Test\n")
            f.write("Kerala,2020,300,Test\n")
            f.write("Chennai,2020,400,Test\n")
            f.write("Kolkata,2020,500,Test\n")

    def test_01_basic_chat_queries(self):
        """Test basic chat queries without user_id"""
        test_queries = [
            "What is the crime rate in Delhi in 2020?",
            "Show me literacy rates in Kerala",
            "AQI levels in Mumbai"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"Basic Chat Query: '{query}'",
                "POST",
                "chat",
                200,
                data={"query": query}
            )
            self.assertTrue(success)
            if success:
                data = response.json()
                self.assertIn("results", data)
                self.assertTrue(len(data["results"]) > 0, f"No results returned for query: {query}")
                
                # Check for error messages in the response
                for result in data["results"]:
                    self.assertIn("insight", result)
                    self.assertNotIn("error", result)
                    self.assertNotIn("TypeError", result["insight"])
                    self.assertNotIn("ObjectId", result["insight"])
                    self.assertNotIn("has no attribute", result["insight"])
                
                print(f"Query: '{query}'")
                print(f"Total results: {len(data['results'])}")
                print(f"First result collection: {data['results'][0]['collection']}")
                print(f"First result insight: {data['results'][0]['insight'][:100]}...")

    def test_02_temporal_queries(self):
        """Test temporal queries with year ranges"""
        test_queries = [
            "Crime trends 2020-2023",
            "Power consumption in Tamil Nadu 2024",
            "AQI trends from 2020 to 2023"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"Temporal Query: '{query}'",
                "POST",
                "chat",
                200,
                data={"query": query}
            )
            self.assertTrue(success)
            if success:
                data = response.json()
                self.assertIn("results", data)
                self.assertTrue(len(data["results"]) > 0, f"No results returned for query: {query}")
                
                # Check for error messages in the response
                for result in data["results"]:
                    self.assertIn("insight", result)
                    self.assertNotIn("error", result)
                    self.assertNotIn("TypeError", result["insight"])
                    self.assertNotIn("ObjectId", result["insight"])
                
                print(f"Query: '{query}'")
                print(f"Total results: {len(data['results'])}")
                print(f"First result collection: {data['results'][0]['collection']}")
                print(f"First result insight: {data['results'][0]['insight'][:100]}...")

    def test_03_multi_state_comparison(self):
        """Test multi-state comparison queries"""
        test_queries = [
            "Compare literacy between Kerala and Punjab",
            "Compare crime rates in Delhi and Mumbai",
            "AQI comparison between Delhi and Mumbai"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"Multi-state Query: '{query}'",
                "POST",
                "chat",
                200,
                data={"query": query}
            )
            self.assertTrue(success)
            if success:
                data = response.json()
                self.assertIn("results", data)
                self.assertTrue(len(data["results"]) > 0, f"No results returned for query: {query}")
                
                # Check for error messages in the response
                for result in data["results"]:
                    self.assertIn("insight", result)
                    self.assertNotIn("error", result)
                    self.assertNotIn("TypeError", result["insight"])
                    self.assertNotIn("ObjectId", result["insight"])
                
                print(f"Query: '{query}'")
                print(f"Total results: {len(data['results'])}")
                print(f"First result collection: {data['results'][0]['collection']}")
                print(f"First result insight: {data['results'][0]['insight'][:100]}...")

    def test_04_objectid_serialization(self):
        """Test the data cleaning and ObjectId removal process"""
        # Test with a query that might return MongoDB ObjectIds
        query = "Show me all data"
        success, response = self.tester.run_test(
            "ObjectId Serialization Test",
            "POST",
            "chat",
            200,
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            self.assertIn("results", data)
            
            # Check if the response can be serialized to JSON
            try:
                json_str = json.dumps(data)
                print(f"Successfully serialized response to JSON ({len(json_str)} characters)")
            except TypeError as e:
                self.fail(f"Failed to serialize response to JSON: {str(e)}")
            
            # Check for ObjectId in the response
            json_str = json.dumps(data)
            self.assertNotIn("ObjectId", json_str)
            
            # Check if all _id fields have been removed
            def check_for_id(obj):
                if isinstance(obj, dict):
                    self.assertNotIn("_id", obj)
                    for key, value in obj.items():
                        if isinstance(value, (dict, list)):
                            check_for_id(value)
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, (dict, list)):
                            check_for_id(item)
            
            check_for_id(data)
            print("No _id fields found in the response")

    def test_05_chat_with_user_data(self):
        """Test chat queries with user_id parameter"""
        # Step 1: Register a new user
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
                
                # Step 3: Upload a test file
                with open(self.test_csv_path, "rb") as f:
                    files = {"file": ("test_data.csv", f, "text/csv")}
                    success, upload_response = self.tester.run_test(
                        "Upload CSV File",
                        "POST",
                        "upload",
                        200,
                        data={},
                        files=files,
                        auth=True
                    )
                self.assertTrue(success)
                if success:
                    upload_data = upload_response.json()
                    self.tester.file_id = upload_data["file_id"]
                    
                    # Step 4: Test chat with user_id parameter
                    test_queries = [
                        "Show me my data",
                        "What data do I have for Delhi?",
                        "Show me my test data"
                    ]
                    
                    for query in test_queries:
                        success, response = self.tester.run_test(
                            f"Chat Query with user_id: '{query}'",
                            "POST",
                            "chat",
                            200,
                            data={"query": query, "user_id": self.tester.user_id}
                        )
                        self.assertTrue(success)
                        if success:
                            data = response.json()
                            self.assertIn("results", data)
                            
                            # Check for 'dict object has no attribute user_id' error
                            json_str = json.dumps(data)
                            self.assertNotIn("has no attribute 'user_id'", json_str)
                            self.assertNotIn("AttributeError", json_str)
                            
                            print(f"Query with user_id: '{query}'")
                            print(f"Total results: {len(data['results'])}")
                            if data["results"]:
                                print(f"First result collection: {data['results'][0]['collection']}")
                                print(f"First result insight: {data['results'][0]['insight'][:100]}...")

    def test_06_error_handling(self):
        """Test comprehensive error handling"""
        # Test invalid queries
        invalid_queries = [
            "",  # Empty query
            "?",  # Single character
            "abcdefghijklmnopqrstuvwxyz"  # Random string
        ]
        
        for query in invalid_queries:
            success, response = self.tester.run_test(
                f"Invalid Chat Query: '{query}'",
                "POST",
                "chat",
                200,  # Should still return 200 with a helpful message
                data={"query": query}
            )
            self.assertTrue(success)
            if success:
                data = response.json()
                self.assertIn("results", data)
                self.assertTrue(len(data["results"]) > 0, "No results returned for invalid query")
                
                # Check that the response contains a helpful message
                first_result = data["results"][0]
                self.assertIn("insight", first_result)
                print(f"Invalid query: '{query}'")
                print(f"Response insight: {first_result['insight'][:100]}...")
        
        # Test non-existent states/years
        non_existent_queries = [
            "Show me crime data for Atlantis",
            "What was the literacy rate in 1800?",
            "AQI in Mars"
        ]
        
        for query in non_existent_queries:
            success, response = self.tester.run_test(
                f"Non-existent Data Query: '{query}'",
                "POST",
                "chat",
                200,  # Should still return 200 with a helpful message
                data={"query": query}
            )
            self.assertTrue(success)
            if success:
                data = response.json()
                self.assertIn("results", data)
                
                # Check that the response contains a helpful message
                first_result = data["results"][0]
                self.assertIn("insight", first_result)
                print(f"Non-existent data query: '{query}'")
                print(f"Response insight: {first_result['insight'][:100]}...")
        
        # Check error response format
        # Test with malformed JSON
        try:
            url = f"{self.tester.base_url}/chat"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data="This is not JSON", headers=headers)
            
            print(f"Malformed JSON test - Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            # Should return 422 or similar for invalid JSON
            self.assertNotEqual(response.status_code, 200)
        except Exception as e:
            print(f"Error testing malformed JSON: {str(e)}")

    def test_07_response_quality(self):
        """Test response quality and content"""
        test_queries = [
            "What are the key findings about crime in Delhi?",
            "What recommendations do you have for improving literacy in Bihar?",
            "What trends do you see in AQI data for Mumbai?"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"Response Quality Test: '{query}'",
                "POST",
                "chat",
                200,
                data={"query": query}
            )
            self.assertTrue(success)
            if success:
                data = response.json()
                self.assertIn("results", data)
                self.assertTrue(len(data["results"]) > 0, f"No results returned for query: {query}")
                
                # Check for quality indicators in the response
                result = data["results"][0]
                self.assertIn("insight", result)
                
                # Check for emojis in the response (indicator of proper formatting)
                insight = result.get("insight", "")
                has_emoji = any(ord(c) > 127 for c in insight)
                
                # Check for key sections
                has_key_findings = "key_findings" in result or "Key Findings" in insight
                has_recommendations = "recommendations" in result or "Recommendations" in insight
                
                print(f"Query: '{query}'")
                print(f"Has emoji formatting: {has_emoji}")
                print(f"Has key findings: {has_key_findings}")
                print(f"Has recommendations: {has_recommendations}")
                print(f"Response insight: {insight[:200]}...")

    def test_08_no_openai_dependency(self):
        """Test that responses are generated without OpenAI API"""
        # This is a bit tricky to test directly, but we can check for indicators
        # that the response is generated from MongoDB data analysis rather than OpenAI
        
        test_queries = [
            "Analyze crime patterns in Delhi",
            "What can you tell me about literacy in India?",
            "Compare AQI across major cities"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"No OpenAI Dependency Test: '{query}'",
                "POST",
                "chat",
                200,
                data={"query": query}
            )
            self.assertTrue(success)
            if success:
                data = response.json()
                self.assertIn("results", data)
                
                # Check for indicators of MongoDB-based analysis
                result = data["results"][0]
                insight = result.get("insight", "")
                
                # OpenAI responses typically don't include these specific phrases
                self.assertNotIn("I'm sorry, I don't have enough information", insight.lower())
                self.assertNotIn("as an ai language model", insight.lower())
                self.assertNotIn("i don't have access to real-time data", insight.lower())
                
                # Check for data-driven indicators
                self.assertIn("data", result)
                self.assertIn("record_count", result)
                
                print(f"Query: '{query}'")
                print(f"Response appears to be data-driven from MongoDB")
                print(f"Response insight: {insight[:200]}...")

    @classmethod
    def tearDownClass(cls):
        # Clean up test file
        if os.path.exists(cls.test_csv_path):
            os.remove(cls.test_csv_path)
        
        cls.tester.print_summary()

if __name__ == "__main__":
    # Create a test suite with just the chat tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTRACITYChatAPI)
    unittest.TextTestRunner(verbosity=2).run(suite)
