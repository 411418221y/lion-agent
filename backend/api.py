from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import numpy as np
from sentence_transformers import SentenceTransformer

app = FastAPI()

# ===== Paths / Config =====

BASE_DIR = Path(__file__).resolve().parent  # backend/
ART = BASE_DIR / "artifacts"
CHUNKS_PATH = ART / "chunks.jsonl"

MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 3
PREVIEW_CHARS = 900

_model: Optional[SentenceTransformer] = None
_chunks: Optional[List[Dict[str, Any]]] = None
_embs: Optional[np.ndarray] = None  # shape: [N, dim], float32


class AskReq(BaseModel):
    question: str


def _load_chunks() -> List[Dict[str, Any]]:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Missing chunks: {CHUNKS_PATH} (run chunker.py first)")

    chunks: List[Dict[str, Any]] = []
    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def _ensure_loaded():
    """
    只在第一次请求时加载：
    - chunks
    - embedding model
    - 所有 chunk 的 embedding 矩阵（纯 numpy）
    """
    global _model, _chunks, _embs

    if _chunks is None:
        _chunks = _load_chunks()

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    if _embs is None:
        texts = [((c.get("text") or "").strip()) for c in _chunks]
        if not any(texts):
            raise ValueError("chunks.jsonl has no non-empty text")

        # 一次性把所有 chunk embed 成矩阵
        _embs = _model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/ask")
def ask(req: AskReq):
    try:
        q = (req.question or "").strip()
        if not q:
            raise HTTPException(status_code=400, detail="Empty question")

        _ensure_loaded()

        # q_emb: [dim]
        q_emb = _model.encode(
            [q],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")[0]

        # cosine / inner product（因为都 normalize 了）
        scores = _embs @ q_emb  # [N]

        # top-k indices
        top_idx = np.argsort(-scores)[:TOP_K]

        hits = []
        for rank, idx in enumerate(top_idx, start=1):
            idx = int(idx)
            c = _chunks[idx]
            score = float(scores[idx])

            text = (c.get("text") or "").strip()
            preview = text[:PREVIEW_CHARS] + ("..." if len(text) > PREVIEW_CHARS else "")

            hits.append({
                "rank": rank,
                "score": score,
                "file": c.get("file"),
                "line_start": c.get("line_start"),
                "line_end": c.get("line_end"),
                "preview": preview,
                "text": text,
            })

        checklist = [
            f"[{h['rank']}] {h['preview']} (score={h['score']:.3f})"
            for h in hits
        ]
        citations = [
            f"{h['file']}  L{h['line_start']}-{h['line_end']}"
            for h in hits
        ]

        return {
            "answer": "Top matches from your policy database:",
            "checklist": checklist,
            "templates": [],
            "risks": [],
            "citations": citations,
            "hits": hits,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ask failed: {e}")


