from pathlib import Path
import json

def chunk_text(lines, chunk_size=900, overlap=150):
    chunks = []
    buf = ""
    cur_start = 1
    for i, line in enumerate(lines, start=1):
        if not buf:
            cur_start = i
        buf += line + "\n"
        if len(buf) >= chunk_size:
            chunks.append((cur_start, i, buf))
            buf = buf[-overlap:]
    if buf.strip():
        chunks.append((cur_start, len(lines), buf))
    return chunks

def build_chunks(curated_dir="backend/data/curated", out_path="backend/artifacts/chunks.jsonl"):
    curated = Path(curated_dir)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as f:
        for fp in sorted(curated.rglob("*.md")):
            lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
            for (ls, le, text) in chunk_text(lines):
                obj = {
                    "file": str(fp),
                    "line_start": ls,
                    "line_end": le,
                    "text": text
                }
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    build_chunks()
    print("✅ Wrote backend/artifacts/chunks.jsonl")
