import requests
import json

# Récupérer le schéma OpenAPI
response = requests.get("http://localhost:8003/openapi.json")
openapi_schema = response.json()

print("=== ENDPOINTS DISPONIBLES DANS RECOBUILDER API ===\n")

# Parcourir tous les paths
for path, methods in openapi_schema.get("paths", {}).items():
    print(f"\n📍 {path}")
    for method, details in methods.items():
        summary = details.get("summary", "No summary")
        print(f"   {method.upper():8} - {summary}")

print("\n" + "="*50)
