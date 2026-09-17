import os
import json
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


ART = Path("backend/artifacts")
INDEX_PATH = ART / "faiss.index"
CHUNKS_PATH = ART / "chunks.jsonl"

MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks():
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def main():
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"Missing index: {INDEX_PATH}")
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Missing chunks: {CHUNKS_PATH}")

    q = input("Ask: ").strip()
    if not q:
        print("Empty query. Bye.")
        return

    k = 3

    index = faiss.read_index(str(INDEX_PATH))
    chunks = load_chunks()

    model = SentenceTransformer(MODEL_NAME)
    q_emb = model.encode([q], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

    D, I = index.search(q_emb, k)

    print("\nTop matches:\n")
    for rank, idx in enumerate(I[0], start=1):
        c = chunks[idx]
        print(f"#{rank}  score={float(D[0][rank-1]):.4f}")
        print(c["text"])
        print("-" * 60)


if __name__ == "__main__":
    main()
    os._exit(0)


