import requests
import json
import sys

def test_chat_api():
    """Test the enhanced chat API functionality"""
    base_url = "https://38c5b002-937f-4add-9333-a54cc7abea8a.preview.emergentagent.com/api"
    
    # Test queries
    test_queries = [
        "What is the crime rate in Delhi in 2020?",
        "Show me literacy rates in Kerala",
        "AQI levels in Mumbai and Bangalore",
        "Power consumption in Tamil Nadu 2023",
        "Compare crime statistics between Delhi and Mumbai"
    ]
    
    print("Testing Enhanced Chat API Functionality\n")
    print(f"API URL: {base_url}/chat\n")
    
    success_count = 0
    
    for query in test_queries:
        print(f"Testing query: '{query}'")
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "results" in data and len(data["results"]) > 0:
                    print(f"✅ Success - Status: {response.status_code}")
                    print(f"Found {len(data['results'])} results")
                    
                    # Check for state-specific data
                    states_found = set()
                    for result in data["results"]:
                        if "state_specific" in result:
                            states_found.add(result["state_specific"])
                    
                    if states_found:
                        print(f"Found data for states: {', '.join(states_found)}")
                    
                    # Check for insights
                    for i, result in enumerate(data["results"]):
                        if "insight" in result:
                            print(f"Result {i+1} insight: {result['insight'][:100]}...")
                            
                            # Check for visual links
                            if "visual_link" in result:
                                print(f"Visual link: {result['visual_link']}")
                    
                    success_count += 1
                else:
                    print(f"❌ Failed - No results found in response")
            else:
                print(f"❌ Failed - Status: {response.status_code}")
                print(f"Error: {response.text}")
        
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
        
        print("-" * 80)
    
    print(f"\nSummary: {success_count}/{len(test_queries)} queries successful")
    
    return success_count == len(test_queries)

if __name__ == "__main__":
    success = test_chat_api()
    sys.exit(0 if success else 1)