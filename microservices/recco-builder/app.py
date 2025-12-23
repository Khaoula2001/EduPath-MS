from flask import Flask, jsonify, request
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_all, create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Resource
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
DB_URL = f"postgresql://{os.getenv('PG_USER', 'prepadata')}:{os.getenv('PG_PASSWORD', 'prepadata_pwd')}@{os.getenv('PG_HOST', 'postgres')}:{os.getenv('PG_PORT', '5432')}/{os.getenv('PG_DB', 'analytics')}"

# Initialize Database
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize Model (BERT)
print("Loading BERT model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384  # MiniLM-L6-v2 output dimension

# Initialize Faiss Index
index = faiss.IndexFlatL2(dimension)
resource_ids = []

def rebuild_index():
    global index, resource_ids
    print("Rebuilding Faiss index...")
    db = SessionLocal()
    try:
        resources = db.query(Resource).all()
        if not resources:
            print("No resources found in DB to index.")
            return

        descriptions = [r.description for r in resources]
        embeddings = model.encode(descriptions)
        
        # New index
        new_index = faiss.IndexFlatL2(dimension)
        new_index.add(np.array(embeddings).astype('float32'))
        
        index = new_index
        resource_ids = [str(r.id) for r in resources]
        print(f"Indexed {len(resources)} resources.")
    except Exception as e:
        print(f"Error rebuilding index: {e}")
    finally:
        db.close()

# Startup initialization
with app.app_context():
    try:
        Base.metadata.create_all(bind=engine)
        rebuild_index()
    except Exception as e:
        print(f"Startup indexing failed (likely DB not ready): {e}")

@app.route('/')
def index_route():
    return jsonify({"service": "RecoBuilder", "status": "running", "indexed_resources": len(resource_ids)})

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    query = data.get('query', '')
    top_k = data.get('top_k', 3)
    student_id = data.get('student_id')
    student_profile = data.get('student_profile') # From StudentProfiler
    risk_level = data.get('risk_level')           # From PathPredictor

    if not query:
        return jsonify({"error": "No query provided"}), 400

    if index.ntotal == 0:
        return jsonify({"error": "Index is empty. No resources available."}), 404

    # Generalization Logic: Augment query based on profile and risk
    augmented_query = query
    
    if risk_level == "High":
        augmented_query += " basic remediation fundamental support"
    elif risk_level == "Medium":
        augmented_query += " reinforcement practice"
    
    if student_profile == "Procrastinateur (Procrastinator)":
        augmented_query += " short engaging interactive video"
    elif student_profile == "Assidu (Regular)":
        augmented_query += " advanced enrichment deeper dive"
    elif student_profile == "En difficulté (At-Risk)":
        augmented_query += " remedial assistance step-by-step"

    print(f"Original Query: {query}")
    print(f"Augmented Query: {augmented_query}")

    # Encode query (using augmented query for better semantic matching)
    query_vector = model.encode([augmented_query])
    
    # Search in Faiss
    distances, indices = index.search(np.array(query_vector).astype('float32'), top_k)
    
    # Map back to resources
    db = SessionLocal()
    recommendations = []
    try:
        for i in indices[0]:
            if i != -1 and i < len(resource_ids):
                res_id = resource_ids[i]
                res = db.query(Resource).filter(Resource.id == res_id).first()
                if res:
                    recommendations.append({
                        "id": str(res.id),
                        "title": res.title,
                        "type": res.type,
                        "url": res.url,
                        "distance": float(distances[0][np.where(indices[0] == i)[0][0]]),
                        "relevance_boosted": augmented_query != query
                    })
    finally:
        db.close()

    return jsonify({
        "student_id": student_id,
        "recommendations": recommendations,
        "metadata": {
            "profile_used": student_profile,
            "risk_used": risk_level,
            "augmented_query": augmented_query
        }
    })

@app.route('/resources', methods=['POST'])
def add_resource():
    data = request.json
    db = SessionLocal()
    try:
        new_res = Resource(
            title=data['title'],
            description=data['description'],
            type=data.get('type', 'other'),
            url=data.get('url', ''),
            tags=data.get('tags', '')
        )
        db.add(new_res)
        db.commit()
        db.refresh(new_res)
        
        # Trigger index rebuild (or update incrementally in prod)
        rebuild_index()
        
        return jsonify({"message": "Resource added", "id": str(new_res.id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route('/health')
def health():
    return jsonify({"status": "ok", "index_size": index.ntotal})

if __name__ == '__main__':
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    app.run(host='0.0.0.0', port=8003)
