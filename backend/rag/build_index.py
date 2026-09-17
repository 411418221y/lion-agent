import json
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

ART = Path("backend/artifacts")
CHUNKS_PATH = ART / "chunks.jsonl"
INDEX_PATH = ART / "faiss.index"
META_PATH = ART / "meta.json"

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 16


def load_chunks(path: Path):
    chunks = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
    return chunks


def ensure_faiss_ready(x: np.ndarray) -> np.ndarray:

    if not isinstance(x, np.ndarray):
        x = np.asarray(x)


    if x.dtype != np.float32:
        x = x.astype(np.float32, copy=False)


    x = np.ascontiguousarray(x)


    if x.ndim == 1:
        x = x.reshape(1, -1)

    return x


def main():
    ART.mkdir(parents=True, exist_ok=True)

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Missing {CHUNKS_PATH}. Run chunker.py first.")

    chunks = load_chunks(CHUNKS_PATH)


    texts = []
    kept_chunks = []
    for c in chunks:
        t = (c.get("text") or "").strip()
        if t:
            texts.append(t)
            kept_chunks.append(c)

    print("Embedding chunks:", len(texts))
    if not texts:
        raise ValueError("No non-empty 'text' found in chunks.jsonl")

    model = SentenceTransformer(MODEL_NAME)

    index = None
    added = 0

    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]


        vecs = model.encode(
            batch_texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        vecs = ensure_faiss_ready(vecs)


        print(
            f"Batch {i//BATCH_SIZE + 1}: shape={vecs.shape}, dtype={vecs.dtype}, "
            f"contig={vecs.flags['C_CONTIGUOUS']}"
        )

        if index is None:
            dim = vecs.shape[1]
            index = faiss.IndexFlatIP(dim)


            test_vec = ensure_faiss_ready(vecs[:1])
            index.add(test_vec)
            added += 1
            print("Warm-up add ok (1 vector).")


            if vecs.shape[0] > 1:
                index.add(vecs[1:])
                added += (vecs.shape[0] - 1)
        else:
            index.add(vecs)
            added += vecs.shape[0]

        print(f"Added {added} / {len(texts)}")

    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(
        json.dumps(kept_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("✅ Index built successfully")
    print("Vectors:", index.ntotal, "Dim:", index.d)

    import os
    os._exit(0)


if __name__ == "__main__":
    main()
