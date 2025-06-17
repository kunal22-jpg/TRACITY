import requests
import unittest
import json
import os
from datetime import datetime

class TRACITYEnhancedChatTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None, auth=False, auth_token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add authorization header if required and available
        if auth and auth_token:
            headers['Authorization'] = f"Bearer {auth_token}"
        
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

class TestEnhancedMongoDBChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get the backend URL from the environment variable
        cls.base_url = "https://38c5b002-937f-4add-9333-a54cc7abea8a.preview.emergentagent.com/api"
        cls.tester = TRACITYEnhancedChatTester(cls.base_url)
        print(f"Testing Enhanced MongoDB-only Chatbot API at: {cls.base_url}")

    def test_01_state_detection(self):
        """Test state detection in queries"""
        test_queries = [
            "What is the crime rate in Delhi?",
            "Show me literacy rates in Kerala",
            "AQI levels in Mumbai",
            "Power consumption in Tamil Nadu",
            "Crime statistics in Uttar Pradesh",
            "Education data for Karnataka"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"State Detection: '{query}'",
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
                
                # Check that the state was correctly detected
                state_name = query.split(" in ")[1].strip("?") if " in " in query else None
                if state_name:
                    # Check if the state name appears in the insight
                    insight = data["results"][0]["insight"]
                    self.assertTrue(
                        state_name.lower() in insight.lower() or 
                        state_name.split()[0].lower() in insight.lower(),
                        f"State '{state_name}' not found in response for query: {query}"
                    )
                
                print(f"Query: '{query}'")
                print(f"Response correctly identified state in query")

    def test_02_year_detection(self):
        """Test year detection in queries"""
        test_queries = [
            "What is the crime rate in Delhi in 2020?",
            "Show me literacy rates in Kerala for 2019",
            "AQI levels in Mumbai during 2022",
            "Power consumption in Tamil Nadu in 2021"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"Year Detection: '{query}'",
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
                
                # Extract year from query
                import re
                years = re.findall(r'\b(20[0-2][0-9])\b', query)
                if years:
                    year = years[0]
                    # Check if the year appears in the insight
                    insight = data["results"][0]["insight"]
                    self.assertIn(year, insight, f"Year '{year}' not found in response for query: {query}")
                
                print(f"Query: '{query}'")
                print(f"Response correctly identified year in query")

    def test_03_collection_detection(self):
        """Test collection detection in queries"""
        test_queries = [
            {"query": "What is the crime rate in Delhi?", "expected_collection": "crimes"},
            {"query": "Show me literacy rates in Kerala", "expected_collection": "literacy"},
            {"query": "AQI levels in Mumbai", "expected_collection": "aqi"},
            {"query": "Power consumption in Tamil Nadu", "expected_collection": "power_consumption"}
        ]
        
        for test in test_queries:
            query = test["query"]
            expected_collection = test["expected_collection"]
            
            success, response = self.tester.run_test(
                f"Collection Detection: '{query}'",
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
                
                # Check that the correct collection was used
                actual_collection = data["results"][0]["collection"]
                self.assertEqual(
                    expected_collection, 
                    actual_collection,
                    f"Expected collection '{expected_collection}' but got '{actual_collection}' for query: {query}"
                )
                
                print(f"Query: '{query}'")
                print(f"Correctly used collection: {actual_collection}")

    def test_04_fallback_search(self):
        """Test fallback search for general queries"""
        test_queries = [
            "Tell me about Indian data",
            "What information do you have?",
            "Show me some statistics"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"Fallback Search: '{query}'",
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
                
                # Check that multiple collections were searched
                self.assertIn("total_collections_searched", data)
                collections_searched = data["total_collections_searched"]
                self.assertGreater(collections_searched, 0, f"No collections searched for query: {query}")
                
                print(f"Query: '{query}'")
                print(f"Collections searched: {collections_searched}")
                print(f"First result collection: {data['results'][0]['collection']}")

    def test_05_response_structure(self):
        """Test response structure with insights, data, and metadata"""
        query = "What is the crime rate in Delhi in 2020?"
        
        success, response = self.tester.run_test(
            f"Response Structure: '{query}'",
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
            
            # Check response structure
            result = data["results"][0]
            self.assertIn("collection", result)
            self.assertIn("insight", result)
            self.assertIn("chart_type", result)
            self.assertIn("data", result)
            self.assertIn("record_count", result)
            
            # Check that data is properly cleaned (no ObjectIds)
            json_str = json.dumps(data)
            self.assertNotIn("ObjectId", json_str)
            
            # Check that insight is not empty
            self.assertGreater(len(result["insight"]), 10)
            
            # Check that data is not empty
            self.assertGreater(len(result["data"]), 0)
            
            print(f"Query: '{query}'")
            print(f"Response has proper structure with insights, data, and metadata")
            print(f"Data sample: {json.dumps(result['data'][0], indent=2)}")

    def test_06_complex_queries(self):
        """Test complex queries with multiple conditions"""
        test_queries = [
            "Compare crime rates in Delhi and Mumbai between 2020 and 2022",
            "Show me literacy trends in Kerala and Tamil Nadu from 2018 to 2022",
            "What are the AQI levels in Delhi, Mumbai, and Bangalore in 2021?"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"Complex Query: '{query}'",
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
                
                # Check that the response contains meaningful data
                result = data["results"][0]
                self.assertIn("insight", result)
                self.assertIn("data", result)
                self.assertGreater(len(result["data"]), 0)
                
                print(f"Query: '{query}'")
                print(f"Response contains meaningful data for complex query")
                print(f"Insight: {result['insight'][:200]}...")

    def test_07_no_openai_indicators(self):
        """Test for indicators that responses are MongoDB-only without OpenAI"""
        test_queries = [
            "What is the crime rate in Delhi?",
            "Show me literacy rates in Kerala",
            "AQI levels in Mumbai"
        ]
        
        for query in test_queries:
            success, response = self.tester.run_test(
                f"No OpenAI Indicators: '{query}'",
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
                
                # Check for indicators that this is MongoDB-only
                result = data["results"][0]
                insight = result["insight"]
                
                # OpenAI responses typically include these phrases
                openai_indicators = [
                    "as an ai language model",
                    "i don't have access to real-time data",
                    "i don't have the ability to",
                    "i cannot access",
                    "i'm not able to"
                ]
                
                for indicator in openai_indicators:
                    self.assertNotIn(indicator, insight.lower())
                
                # Check for data-driven indicators
                self.assertIn("data", result)
                self.assertIn("record_count", result)
                
                print(f"Query: '{query}'")
                print(f"Response appears to be MongoDB-only without OpenAI")

    def test_08_data_cleaning(self):
        """Test data cleaning to ensure no ObjectIds are present"""
        query = "Show me all available data"
        
        success, response = self.tester.run_test(
            f"Data Cleaning: '{query}'",
            "POST",
            "chat",
            200,
            data={"query": query}
        )
        self.assertTrue(success)
        if success:
            data = response.json()
            
            # Try to serialize the entire response to JSON
            try:
                json_str = json.dumps(data)
                print(f"Successfully serialized response to JSON ({len(json_str)} characters)")
            except TypeError as e:
                self.fail(f"Failed to serialize response to JSON: {str(e)}")
            
            # Check for ObjectId in the response
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
            print("No _id fields or ObjectIds found in the response")

    @classmethod
    def tearDownClass(cls):
        cls.tester.print_summary()

if __name__ == "__main__":
    # Create a test suite with just the enhanced MongoDB chatbot tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedMongoDBChatbot)
    unittest.TextTestRunner(verbosity=2).run(suite)