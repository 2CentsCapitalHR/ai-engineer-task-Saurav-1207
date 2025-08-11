# build_rag_sentence_transformers.py
# Usage:
#   pip install sentence-transformers faiss-cpu bs4 requests
#   python build_rag_sentence_transformers.py --data-sources data_sources.txt --out adgm_index_data.pkl

import argparse, pickle, requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

def fetch_text(url):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for s in soup(['script', 'style', 'noscript']):
            s.decompose()
        return soup.get_text(separator="\n")
    except Exception as e:
        print(f"Failed {url}: {e}")
        return ""

def chunk_text(text, chunk_size=400, overlap=80):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-sources", required=True, help="Text file with one URL per line")
    ap.add_argument("--out", default="adgm_index_data.pkl", help="Output pickle file")
    ap.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model")
    args = ap.parse_args()

    # Read URLs
    with open(args.data_sources, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Fetching {len(urls)} URLs...")
    docs = []
    for u in urls:
        txt = fetch_text(u)
        if txt:
            docs.append({"url": u, "text": txt})

    # Chunking
    chunks, metadata = [], []
    for doc in docs:
        for ci, ch in enumerate(chunk_text(doc["text"])):
            chunks.append(ch)
            metadata.append({"url": doc["url"], "chunk_index": ci, "excerpt": ch[:300]})

    print(f"Created {len(chunks)} chunks.")

    # Embeddings
    print("Encoding embeddings...")
    model = SentenceTransformer(args.model)
    embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)

    # Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    # Save
    with open(args.out, "wb") as f:
        pickle.dump({
            "chunks": chunks,
            "metadata": metadata,
            "index_flat": index,
            "dimension": dim
        }, f)

    print(f"Saved index to {args.out}")

if __name__ == "__main__":
    main()
