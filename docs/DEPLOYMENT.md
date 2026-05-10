# Deployment guide — AFOIS

This backend is container-first (`Dockerfile` + `docker/entrypoint.sh`: **Alembic migrate → Uvicorn**). The frontend (`web/`) is a separate **Next.js** process — use **`/afois-api`** rewrites pointing at your public API origin.

---

## Environment checklist

| Surface | Critical vars |
|---------|----------------|
| **API** | `DATABASE_URL`, `PYTHONPATH=/app/src` (Docker already sets), **`OPENAI_API_KEY`** and/or **`GEMINI_API_KEY`**, **`CHROMA_PERSIST_DIRECTORY`** on **persistent disk** |
| **API** resilience | **`LLM_AUTO_FAILOVER=true`**, **`LLM_RATE_LIMIT_FALLBACK_REPLY`** (demo-friendly), optional **`GEMINI_FALLBACK_MODEL`** |
| **Web** build | **`AFOIS_BACKEND_URL`** = HTTPS URL of the API (**server-side rewrite target** — never bake secrets into browser) |

Optional: **`ADMIN_REINDEX_TOKEN`** + header for `POST /v1/rag/rebuild`, **`CORS_ALLOWED_ORIGINS`** if you intentionally call API directly from browsers (prefer proxy).

---

## Render

1. New **Blueprint** → select **`render.yaml`** from this repo.  
2. Dashboard → enter secrets: **`DATABASE_URL`**, keys, **`LLM_RATE_LIMIT_FALLBACK_REPLY`**, **`OPENAI_*`/`GEMINI_*`**.  
3. Disk is provisioned under **`CHROMA_PERSIST_DIRECTORY=/var/data/chroma_db`** per blueprint.  
4. Health checks: **`/health`** (liveness) · **`/v1/ops/ready`** optional for stricter probes.  
5. Post-deploy: shell into service → **`python scripts/seed_sample_data.py`** and **`python scripts/sync_chroma_policies.py`**.

Frontend: deploy `web/` as a **second Render Web Service** (Node) using **`npm run build` / `npm start`**, **`AFOIS_BACKEND_URL`** = internal or public Render API URL.

---

## Railway

1. New project → **Deploy from Dockerfile** (repo root).  
2. Attach a **persistent volume**, mount path matching **`CHROMA_PERSIST_DIRECTORY`**.  
3. Set **`PORT`** implicitly (Railway sets `PORT`; FastAPI Dockerfile exposes **8000** — Railway maps automatically). Verify **`DATABASE_URL`** is Railway Postgres Plugin URL.  

See optional **[`railway.toml`](../railway.toml)** hints in repo root if present.

---

## Docker VPS / bare metal

```bash
docker build -t afois-api .
docker run -d --restart unless-stopped \
  -e DATABASE_URL=postgresql+psycopg://... \
  -e OPENAI_API_KEY=sk-... \
  -v afois-chroma:/data/chroma_db \
  -e CHROMA_PERSIST_DIRECTORY=/data/chroma_db \
  -p 8000:8000 \
  afois-api
```

Put **nginx/Caddy** in front with TLS termination. Do **not** expose **`POST /v1/rag/rebuild`** without **`ADMIN_REINDEX_TOKEN`**.

Host **Next**: `docker compose --profile frontend` patterns or `node:22-bookworm-slim` with `npm ci && npm run build && npm start`, **`AFOIS_BACKEND_URL`** = `http://api:8000` (Compose) or public URL.

---

## AWS (conceptual)

- **ECS/Fargate** task from this `Dockerfile`.  
- **RDS Postgres** (`DATABASE_URL`).  
- **EFS** bind mount → **`CHROMA_PERSIST_DIRECTORY`**.  
- Secrets Manager → keys + **`ADMIN_REINDEX_TOKEN`**.  
- Target group **HTTP health** `/health`.  
- **CloudFront → S3 / Next standalone** pattern for SPA-style hosting of `web/`.

---

## Verification

After deploy:

```bash
curl -sfS https://YOUR_API/health
curl -sfS https://YOUR_API/v1/ops/ready
curl -sfS https://YOUR_API/v1/ops/llm-config | jq .
```
