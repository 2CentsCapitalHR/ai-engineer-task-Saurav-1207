# rag_index.py
import pickle
import numpy as np

class RagIndex:
    def __init__(self):
        self.chunks = []
        self.metadata = []
        self.index = None
        self.dimension = None

    def load_from_pickle(self, path):
        """Load FAISS index and metadata from a pickle file."""
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.chunks = data["chunks"]
        self.metadata = data["metadata"]
        self.index = data["index_flat"]
        self.dimension = data["dimension"]
        print(f"Loaded RAG index with {len(self.chunks)} chunks.")

    def query(self, vector, k=3):
        """Search for nearest chunks given an embedding vector."""
        if self.index is None:
            raise RuntimeError("Index not loaded.")
        v = np.array(vector, dtype="float32").reshape(1, -1)
        D, I = self.index.search(v, k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if 0 <= idx < len(self.chunks):
                results.append({
                    "chunk": self.chunks[idx],
                    "metadata": self.metadata[idx],
                    "distance": float(dist)
                })
        return results
