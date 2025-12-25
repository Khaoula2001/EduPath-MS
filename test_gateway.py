import requests
import json

BASE_URL = "http://localhost:4000"

def test_health():
    print("\n--- Testing API Gateway Health ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_proxy_reco():
    print("\n--- Testing Proxy to RecoBuilder via Gateway ---")
    try:
        # Testing through the /api/recommendations prefix
        response = requests.get(f"{BASE_URL}/api/recommendations/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_health()
    test_proxy_reco()
