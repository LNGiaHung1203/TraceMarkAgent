import requests
import json

def test_uspto_api():
    """Test the USPTO Trademark API from RapidAPI"""
    print("🔍 Testing USPTO Trademark API from RapidAPI...")
    print("=" * 60)
    
    # RapidAPI configuration - use the GET endpoint with path parameters
    url = "https://uspto-trademark.p.rapidapi.com/v1/trademarkSearch/amazon/all"
    
    rapidapi_key = "9828ed309cmshb004afefdfdc1f0p16cf20jsnec9acd6f365b"  # Your actual key
    
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "uspto-trademark.p.rapidapi.com"
    }
    
    print("🎯 Testing trademark search for: starbucks (active status)")
    print(f"🔗 API Endpoint: {url}")
    print(f"📤 Method: GET with path parameters")
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API call successful!")
            
            try:
                data = response.json()
                print(f"📊 Response data structure:")
                print(f"   - Count: {data.get('count', 'N/A')}")
                print(f"   - Start Index: {data.get('start_index', 'N/A')}")
                print(f"   - Next Index: {data.get('next_index', 'N/A')}")
                
                if 'results' in data and len(data['results']) > 0:
                    print(f"   - Results found: {len(data['results'])}")
                    
                    # Show first result details
                    first_result = data['results'][0]
                    print(f"\n📋 First Result Details:")
                    print(f"   - Keyword: {first_result.get('keyword', 'N/A')}")
                    print(f"   - Serial Number: {first_result.get('serial_number', 'N/A')}")
                    print(f"   - Status: {first_result.get('status_label', 'N/A')}")
                    print(f"   - Filing Date: {first_result.get('filing_date', 'N/A')}")
                    print(f"   - Registration Date: {first_result.get('registration_date', 'N/A')}")
                    
                    # Show owner information if available
                    if 'owners' in first_result and len(first_result['owners']) > 0:
                        owner = first_result['owners'][0]
                        print(f"   - Owner: {owner.get('name', 'N/A')}")
                        print(f"   - Owner Type: {owner.get('owner_label', 'N/A')}")
                    
                else:
                    print("   - No results found")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"📄 Raw response: {response.text[:500]}...")
                
        elif response.status_code == 401:
            print("❌ Unauthorized - Check your RapidAPI key")
        elif response.status_code == 403:
            print("❌ Forbidden - Check your RapidAPI subscription")
        elif response.status_code == 429:
            print("❌ Rate limited - Too many requests")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"📄 Response content: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_multiple_endpoints():
    """Test multiple USPTO API endpoints"""
    print("\n🔍 Testing multiple USPTO API endpoints...")
    print("=" * 60)
    
    rapidapi_key = "9828ed309cmshb004afefdfdc1f0p16cf20jsnec9acd6f365b"  # Your actual key
    
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "uspto-trademark.p.rapidapi.com"
    }
    
    # Test different endpoints - use the correct GET format with path parameters
    endpoints = [
        {
            "name": "Trademark Search - Amazon (active)",
            "url": "https://uspto-trademark.p.rapidapi.com/v1/trademarkSearch/amazon/active",
            "method": "GET"
        },
        {
            "name": "Trademark Search - Apple (all)",
            "url": "https://uspto-trademark.p.rapidapi.com/v1/trademarkSearch/apple/all",
            "method": "GET"
        },
        {
            "name": "Serial Number Search",
            "url": "https://uspto-trademark.p.rapidapi.com/v1/serialSearch/90709119",
            "method": "GET"
        },
        {
            "name": "Database Status",
            "url": "https://uspto-trademark.p.rapidapi.com/v1/databaseStatus",
            "method": "GET"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing: {endpoint['name']}")
        try:
            response = requests.get(endpoint['url'], headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Success!")
                try:
                    data = response.json()
                    if 'count' in data:
                        print(f"   📊 Count: {data['count']}")
                    elif 'database_status' in data:
                        print(f"   📊 Database Status: {data['database_status']}")
                    elif 'results' in data:
                        print(f"   📊 Results: {len(data['results'])} found")
                except:
                    pass
            else:
                print(f"   ❌ Failed - {response.status_code}")
                if response.text:
                    print(f"   📄 Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")

def search_trademarks(keyword, status="active", start_index=0):
    """Search for trademarks using the USPTO API"""
    print(f"\n🎯 Searching for trademarks: {keyword} (status: {status})")
    print("=" * 60)
    
    rapidapi_key = "9828ed309cmshb004afefdfdc1f0p16cf20jsnec9acd6f365b"  # Your actual key
    
    # Use GET endpoint with path parameters as shown in the curl example
    url = f"https://uspto-trademark.p.rapidapi.com/v1/trademarkSearch/{keyword}/{status}"
    
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "uspto-trademark.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ API call failed with status: {response.status_code}")
            print(f"📄 Error: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 USPTO Trademark API Test Script")
    print("=" * 60)
    print("📋 This script tests the USPTO Trademark API from RapidAPI")
    print("🔑 You need to get your API key from: https://rapidapi.com/marton-kodok/api/uspto-trademark/")
    print("💡 The API is free for basic usage (1000 requests/month)")
    print()
    
    # Test the main API functionality
    test_uspto_api()
    
    # Test multiple endpoints
    test_multiple_endpoints()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Get your RapidAPI key from: https://rapidapi.com/marton-kodok/api/uspto-trademark/")
    print("2. Replace 'YOUR_RAPIDAPI_KEY_HERE' with your actual key")
    print("3. Run the script again to test the API")
    print("4. The API provides comprehensive USPTO trademark data")
    print("5. Much more reliable than the previous markerapi.com")
