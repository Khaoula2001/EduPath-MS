import requests
import time

URL = "http://localhost:8003/resources"

resources = [
    {
        "title": "Introduction to Python loops",
        "description": "Learn how to use for and while loops in Python with practical examples.",
        "type": "video",
        "url": "http://minio:9000/content/python_loops.mp4",
        "tags": "python,programming,loops"
    },
    {
        "title": "Understanding SQL Joins",
        "description": "A comprehensive guide to INNER, LEFT, RIGHT and FULL OUTER joins in SQL.",
        "type": "pdf",
        "url": "http://minio:9000/content/sql_joins.pdf",
        "tags": "sql,database,joins"
    },
    {
        "title": "Machine Learning Basics",
        "description": "An introductory course on supervised and unsupervised learning algorithms.",
        "type": "course",
        "url": "http://minio:9000/content/ml_basics.html",
        "tags": "ml,data-science,basics"
    },
    {
        "title": "Linear Algebra for Data Science",
        "description": "Essential linear algebra concepts for understanding machine learning models.",
        "type": "video",
        "url": "http://minio:9000/content/linear_algebra.mp4",
        "tags": "math,ml,data-science"
    },
    {
        "title": "React Hooks Tutorial",
        "description": "Master useState, useEffect and other common React hooks in this hands-on tutorial.",
        "type": "video",
        "url": "http://minio:9000/content/react_hooks.mp4",
        "tags": "react,javascript,frontend"
    }
]

def seed():
    print("Seeding resources...")
    for res in resources:
        try:
            response = requests.post(URL, json=res)
            if response.status_code == 200:
                print(f"Added: {res['title']}")
            else:
                print(f"Failed to add {res['title']}: {response.text}")
        except Exception as e:
            print(f"Error connecting to service: {e}")
            print("Is the service running on http://localhost:8003?")

if __name__ == "__main__":
    seed()
