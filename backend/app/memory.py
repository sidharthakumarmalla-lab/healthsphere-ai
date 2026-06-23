import os
import json
import logging
import numpy as np
from google import genai
from backend.app.config import CHROMA_PERSIST_DIR, GEMINI_API_KEY

logger = logging.getLogger("healthsphere.memory")

# Initialize Gemini Client for embeddings
def get_gemini_client():
    if not GEMINI_API_KEY:
        # Fallback if key is not loaded yet in some environment
        key = os.getenv("GEMINI_API_KEY")
        return genai.Client(api_key=key)
    return genai.Client(api_key=GEMINI_API_KEY)

# Try importing chromadb
CHROMA_AVAILABLE = False
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    logger.warning("chromadb not found. Falling back to SQLite-based Vector Memory.")

class VectorMemory:
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.fallback_db_path = os.path.join(os.path.dirname(CHROMA_PERSIST_DIR), "fallback_vector_memory.json")
        
        if CHROMA_AVAILABLE:
            try:
                os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
                # We use manual embeddings generated via Gemini to avoid Chroma downloading local transformers
                self.collection = self.chroma_client.get_or_create_collection(
                    name="encounter_memory"
                )
                logger.info("ChromaDB persistent client initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing ChromaDB: {e}. Falling back to SQLite-based Vector Memory.")
                self.chroma_client = None
                self.collection = None

    def _get_embedding(self, text: str) -> list:
        try:
            client = get_gemini_client()
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error generating embedding from Gemini: {e}")
            # Return a mock vector of 768 dimensions if embeddings fail
            return [0.0] * 768

    def add_encounter(self, encounter_id: int, profile_id: int, symptom_summary: str):
        embedding = self._get_embedding(symptom_summary)
        doc_id = f"encounter_{encounter_id}"
        metadata = {
            "encounter_id": encounter_id,
            "profile_id": profile_id,
            "summary": symptom_summary
        }

        if self.collection:
            try:
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[symptom_summary]
                )
                logger.info(f"Encounter {encounter_id} stored in ChromaDB.")
                return
            except Exception as e:
                logger.error(f"Failed to add to ChromaDB: {e}. Falling back to JSON storage.")

        # Fallback: Save to JSON file
        self._add_fallback(doc_id, embedding, metadata, symptom_summary)

    def search_similar_encounters(self, profile_id: int, current_symptoms: str, limit: int = 3) -> list:
        query_embedding = self._get_embedding(current_symptoms)

        if self.collection:
            try:
                # Query ChromaDB. We filter by profile_id to get only this family member's history!
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where={"profile_id": profile_id}
                )
                
                output = []
                if results and 'metadatas' in results and len(results['metadatas']) > 0:
                    for i in range(len(results['metadatas'][0])):
                        meta = results['metadatas'][0][i]
                        distance = results['distances'][0][i] if 'distances' in results else 0.0
                        # Chroma distance: lower is better (usually L2)
                        output.append({
                            "encounter_id": meta["encounter_id"],
                            "profile_id": meta["profile_id"],
                            "summary": meta["summary"],
                            "similarity_score": float(1.0 / (1.0 + distance)) # Convert distance to pseudo-similarity
                        })
                return output
            except Exception as e:
                logger.error(f"ChromaDB query failed: {e}. Trying fallback vector search.")

        # Fallback manual Cosine Similarity
        return self._search_fallback(profile_id, query_embedding, limit)

    def _add_fallback(self, doc_id: str, embedding: list, metadata: dict, document: str):
        data = {}
        if os.path.exists(self.fallback_db_path):
            try:
                with open(self.fallback_db_path, 'r') as f:
                    data = json.load(f)
            except Exception:
                data = {}

        data[doc_id] = {
            "embedding": embedding,
            "metadata": metadata,
            "document": document
        }

        try:
            with open(self.fallback_db_path, 'w') as f:
                json.dump(data, f)
            logger.info(f"Encounter {metadata['encounter_id']} stored in fallback vector storage.")
        except Exception as e:
            logger.error(f"Failed to write fallback storage file: {e}")

    def _search_fallback(self, profile_id: int, query_embedding: list, limit: int) -> list:
        if not os.path.exists(self.fallback_db_path):
            return []

        try:
            with open(self.fallback_db_path, 'r') as f:
                data = json.load(f)
        except Exception:
            return []

        matches = []
        q_vec = np.array(query_embedding)
        q_norm = np.linalg.norm(q_vec)

        for doc_id, item in data.items():
            meta = item["metadata"]
            if meta["profile_id"] != profile_id:
                continue

            doc_vec = np.array(item["embedding"])
            doc_norm = np.linalg.norm(doc_vec)
            
            if q_norm > 0 and doc_norm > 0:
                similarity = float(np.dot(q_vec, doc_vec) / (q_norm * doc_norm))
            else:
                similarity = 0.0

            matches.append({
                "encounter_id": meta["encounter_id"],
                "profile_id": meta["profile_id"],
                "summary": meta["summary"],
                "similarity_score": similarity
            })

        # Sort by similarity score descending
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:limit]

# Global vector memory instance
memory_store = VectorMemory()
