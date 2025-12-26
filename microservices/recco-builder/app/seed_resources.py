import uuid
from app.core.database import SessionLocal, engine, Base
from app.models.domain import Resource
from app.services.embeddings import embedding_service

def seed_resources():
    db = SessionLocal()
    try:
        resources_data = [
            # Architecture
            {
                "title": "Les composants d’un ordinateur – Guide illustré",
                "description": "Guide complet sur le hardware : CPU, RAM, Carte mère et stockage.",
                "type": "pdf",
                "url": "https://moodle.example.com/resource/comp-pc.pdf",
                "tags": "hardware, architecture, débutant"
            },
            {
                "title": "Comprendre CPU, RAM, stockage en 10 minutes",
                "description": "Vidéo explicative sur le fonctionnement interne d'un ordinateur.",
                "type": "video",
                "url": "https://youtube.com/watch?v=pc-basics",
                "tags": "hardware, architecture, vidéo"
            },
            # Algorithmique
            {
                "title": "Les bases du pseudo-code (IF, FOR, WHILE…)",
                "description": "Apprendre à écrire des algorithmes structurés sans code complexe.",
                "type": "pdf",
                "url": "https://moodle.example.com/resource/algo-bases.pdf",
                "tags": "algorithme, programmation, logique"
            },
            {
                "title": "Algorithmes expliqués simplement avec des exemples",
                "description": "Introduction visuelle aux concepts de boucles et conditions.",
                "type": "video",
                "url": "https://youtube.com/watch?v=algo-simples",
                "tags": "algorithme, débutant, vidéo"
            },
            # Web
            {
                "title": "Créer sa première page web",
                "description": "Tutoriel pas à pas pour HTML5 et CSS3.",
                "type": "video",
                "url": "https://youtube.com/watch?v=ma-premiere-page",
                "tags": "web, html, css"
            },
            {
                "title": "Les balises HTML indispensables",
                "description": "Cheat sheet et explications sur les balises de structure.",
                "type": "pdf",
                "url": "https://moodle.example.com/resource/html-tags.pdf",
                "tags": "web, html, documentation"
            },
            # Réseaux
            {
                "title": "Introduction au modèle OSI et TCP/IP",
                "description": "Comprendre les couches réseau et la communication internet.",
                "type": "pdf",
                "url": "https://moodle.example.com/resource/osi-model.pdf",
                "tags": "réseaux, cisco, osi"
            },
            {
                "title": "Adresse IP et sous-réseaux",
                "description": "Guide pratique sur l'adressage IPv4 et le calcul de masques.",
                "type": "video",
                "url": "https://youtube.com/watch?v=ip-subnetting",
                "tags": "réseaux, ip, tutoriel"
            }
        ]

        for r_data in resources_data:
            # Check if exists
            exists = db.query(Resource).filter(Resource.title == r_data["title"]).first()
            if not exists:
                res = Resource(
                    id=uuid.uuid4(),
                    title=r_data["title"],
                    description=r_data["description"],
                    type=r_data["type"],
                    url=r_data["url"],
                    tags=r_data["tags"]
                )
                db.add(res)
        
        db.commit()
        print(f"Successfully seeded {len(resources_data)} resources.")
        
        # Rebuild index
        print("Rebuilding FAISS index...")
        embedding_service.rebuild_index(db)
        print("Index rebuilt.")

    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_resources()
