import requests
import io

# Test simple upload
BASE_URL = "http://localhost:8003"

print("Testing file upload to RecoBuilder...")

# Create a simple in-memory file
file_content = b"This is a test document about artificial intelligence and machine learning."
file_obj = io.BytesIO(file_content)

# Prepare the multipart form data
files = {
    'file': ('test_document.txt', file_obj, 'text/plain')
}

data = {
    'title': 'Test AI Document',
    'description': 'A test document about AI',
    'type': 'document',
    'tags': 'ai,test'
}

print(f"\nSending POST request to {BASE_URL}/resources")
print(f"Data: {data}")

try:
    response = requests.post(
        f"{BASE_URL}/resources",
        files=files,
        data=data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ Upload successful!")
        result = response.json()
        print(f"Resource ID: {result.get('id')}")
        print(f"MinIO URL: {result.get('url')}")
    else:
        print(f"\n✗ Upload failed!")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
