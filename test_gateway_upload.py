import requests
import io

# Test upload through Gateway
BASE_URL = "http://localhost:4000/api/recommendations"

print("Testing file upload to RecoBuilder via Gateway...")

# Create a simple in-memory file
file_content = b"This is a test document uploaded through the API Gateway."
file_obj = io.BytesIO(file_content)

# Prepare the multipart form data
files = {
    'file': ('gateway_test.txt', file_obj, 'text/plain')
}

data = {
    'title': 'Gateway Test Document',
    'description': 'Uploaded via API Gateway',
    'type': 'document',
    'tags': 'gateway,test'
}

print(f"\nSending POST request to {BASE_URL}/resources")

try:
    response = requests.post(
        f"{BASE_URL}/resources",
        files=files,
        data=data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ Upload successful via Gateway!")
    else:
        print(f"\n✗ Upload failed via Gateway!")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
