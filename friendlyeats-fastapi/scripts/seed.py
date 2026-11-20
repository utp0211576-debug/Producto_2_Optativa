import json
import os
from google.cloud import firestore

# Credencial oficial de Firebase
CREDENTIALS_FILE = os.path.abspath("serviceAccountKey.json")

# Quitar cualquier variable del emulador
if "FIRESTORE_EMULATOR_HOST" in os.environ:
    del os.environ["FIRESTORE_EMULATOR_HOST"]

if os.path.exists(CREDENTIALS_FILE):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE
    with open(CREDENTIALS_FILE, "r") as f:
        key_data = json.load(f)
        project_id = key_data.get("project_id", "basedatos-97124")
else:
    print("❌ No se encontró serviceAccountKey.json")
    exit(1)

print(f"📡 Conectando a Firebase Cloud -> Proyecto: {project_id}")
db = firestore.Client(project=project_id)

SAMPLE_IMAGES = [
    "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600",
    "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600",
    "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600",
    "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600",
    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600"
]

RESTAURANTS = [
    {"name": "Pizzeria Luigi", "category": "Italiana", "city": "Guadalajara", "price": 3, "photo": SAMPLE_IMAGES[0], "numRatings": 10, "avgRating": 4.5},
    {"name": "Sushi Roll", "category": "Japonesa", "city": "Monterrey", "price": 4, "photo": SAMPLE_IMAGES[1], "numRatings": 22, "avgRating": 4.8},
    {"name": "Tacos El Pastor", "category": "Mexicana", "city": "CDMX", "price": 2, "photo": SAMPLE_IMAGES[2], "numRatings": 15, "avgRating": 4.7},
    {"name": "Moyuelo", "category": "Contemporánea", "city": "Puebla", "price": 3, "photo": SAMPLE_IMAGES[3], "numRatings": 18, "avgRating": 4.6},
    {"name": "Casa Reyna", "category": "Poblana", "city": "Puebla", "price": 4, "photo": SAMPLE_IMAGES[4], "numRatings": 28, "avgRating": 4.8}
]

def seed_database():
    collection_ref = db.collection("restaurants")
    
    # 1. Limpiar colección anterior
    docs = collection_ref.stream()
    for doc in docs:
        doc.reference.delete()

    # 2. Insertar registros
    for data in RESTAURANTS:
        doc_ref = collection_ref.add(data)
        print(f"  └─ Insertado: {data['name']}")
        
    print(f"\n✅ ¡Población de datos completa en el proyecto {project_id}!")

if __name__ == "__main__":
    seed_database()