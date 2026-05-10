# Security

## Reporting

If you discover a security issue, please open a **private** advisory or contact the repository owner directly. Do not file public issues for undisclosed vulnerabilities.

## Deployment hygiene

- Never commit `.env` or API keys. Rotate any key that was exposed in chat, logs, or screenshots.
- Treat `POST /v1/rag/rebuild` as privileged: protect it with `ADMIN_REINDEX_TOKEN` and network controls.
- Run the API with least-privilege database credentials in production.
- Prefer managed secrets (Render env, AWS Secrets Manager, etc.) over plain text env files on servers.

## LLM & data

- LLM providers may process prompts according to their terms; do not send regulated PII in demo payloads.
- RAG corpus is loaded from your own `policy_documents` table; sanitize content before indexing public demos.
