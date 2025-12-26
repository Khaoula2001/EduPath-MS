import requests
import os
import uuid

# Configuration
# Si vous testez depuis votre machine locale, utilisez localhost:8003
# Si vous testez via l'API Gateway, utilisez localhost:4000/recco/... (si configuré)
BASE_URL = "http://localhost:8003"
TEST_FILE_NAME = f"test_doc_{uuid.uuid4().hex[:6]}.txt"

def run_tests():
    print(f"=== DÉBUT DES TESTS RECCO-BUILDER sur {BASE_URL} ===")

    # 1. Création d'un fichier de test temporaire
    with open(TEST_FILE_NAME, "w") as f:
        f.write("Ceci est un contenu de test pour l'IA et MinIO. L'intelligence artificielle est passionnante.")

    resource_id = None

    try:
        # --- TEST 1: Santé du service ---
        print("\n1. Test Health Check...")
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=5)
            print(f"Status: {r.status_code} | Response: {r.json()}")
        except Exception as e:
            print(f"Erreur de connexion (Le service est-il lancé ?) : {e}")
            return

        # --- TEST 2: Ajouter une ressource (POST /resources) ---
        print("\n2. Test Ajout Ressource (Workflow TeacherConsole)...")
        try:
            with open(TEST_FILE_NAME, "rb") as f:
                files = {"file": (TEST_FILE_NAME, f, "text/plain")}
                data = {
                    "title": "Introduction à l'IA",
                    "description": "Un cours complet sur les bases de l'intelligence artificielle et du machine learning.",
                    "type": "document",
                    "tags": "ia,machine-learning,cours"
                }
                r = requests.post(f"{BASE_URL}/resources", data=data, files=files)
            
            if r.status_code == 200:
                res_data = r.json()
                resource_id = res_data.get("id")
                print(f"Status: {r.status_code}")
                print(f"ID créé: {resource_id}")
                print(f"URL MinIO: {res_data.get('url')}")
            else:
                print(f"Erreur lors de l'ajout: {r.status_code} | {r.text}")
        except Exception as e:
            print(f"Erreur lors de l'upload: {e}")

        # --- TEST 3: Recommandation (POST /recommend) ---
        print("\n3. Test Recommandation (Workflow StudentCoach)...")
        recco_payload = {
            "query": "intelligence artificielle",
            "top_k": 3,
            "student_id": "std_999",
            "student_profile": "Assidu (Regular)",
            "risk_level": "Low"
        }
        r = requests.post(f"{BASE_URL}/recommend", json=recco_payload)
        if r.status_code == 200:
            data = r.json()
            reccos = data.get('recommendations', [])
            print(f"Status: {r.status_code}")
            print(f"Nombre de résultats: {len(reccos)}")
            if len(reccos) > 0:
                print(f"Première recommandation: {reccos[0]['title']} (Score: {reccos[0]['distance']})")
            print(f"Requête augmentée par l'IA: {data.get('metadata', {}).get('augmented_query')}")
        else:
            print(f"Erreur recommandation: {r.status_code} | {r.text}")

    except Exception as e:
        print(f"\nERREUR CRITIQUE: {e}")
    finally:
        # Nettoyage du fichier local
        if os.path.exists(TEST_FILE_NAME):
            os.remove(TEST_FILE_NAME)

    print("\n=== FIN DES TESTS ===")

if __name__ == "__main__":
    run_tests()