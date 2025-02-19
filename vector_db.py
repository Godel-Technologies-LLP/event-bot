import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Service Data
services = [
    {"service": "Photography", "category": "Exhibition", "price": "500 AED"},
    {"service": "Videography", "category": "Annual Party", "price": "400 AED"},
    {"service": "360 Spinner", "category": "Conference", "price": "300 AED"},
    {"service": "Photo Booth", "category": "Birthday Party", "price": "200 AED"},
    {"service": "Mirror Booth", "category": "Anniversary", "price": "350 AED"}
]

# Save services as JSON
with open("services.json", "w") as f:
    json.dump(services, f)

# Convert service details to embeddings
service_texts = [f"{s['service']} for {s['category']}" for s in services]
embeddings = model.encode(service_texts).astype('float32')

# Create FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save FAISS index
faiss.write_index(index, "faiss_index.index")
print("✅ FAISS index created and saved!")

# Load FAISS index & retrieve best service
def retrieve_service(service_query, event_query):
    """Retrieve the best matching service using FAISS."""
    query_text = f"{service_query} for {event_query}"
    query_embedding = model.encode([query_text]).astype('float32')

    # Load FAISS index
    index = faiss.read_index("faiss_index.index")

    # Search for best match
    _, indices = index.search(query_embedding, 1)
    best_match = services[indices[0][0]]
    
    return best_match
