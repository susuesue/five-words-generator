# AGENTS.md

## Cursor Cloud specific instructions

This is a single-service Python FastAPI application ("五大需求提取器" / Five Needs Extractor) that calls the DeepSeek LLM API. No database, Docker, or frontend required.

### Running the service

- **Start server:** `python3 src/api/app_fastapi.py` (listens on port 8080)
- **Swagger docs:** `http://localhost:8080/docs`
- **Health check:** `GET http://localhost:8080/health`
- The `DEEPSEEK_API_KEY` environment variable is required for the `/extract` endpoints to return real results. Without it, the server starts fine but extraction returns empty fields (graceful degradation).
- Copy `.env.example` to `.env` and set your API key there; the app loads it via `python-dotenv`.

### Linting and testing

- **Lint:** `python3 -m flake8 src/ --max-line-length=120`
- **Test:** `python3 -m pytest tests/ -v` — note: `tests/test_generator.py` references a non-existent module `src.core.generator` (stale from an older project iteration). CI runs `pytest tests/ -v || true`.
- Dev dependencies not in `requirements.txt`: `pytest`, `flake8`.

### Gotchas

- `src/api/__init__.py` imports `from .app import app` but the actual file is `app_fastapi.py`. Do not import the `src.api` package directly; run the server via `python3 src/api/app_fastapi.py`.
- `config.py` defines `FASTAPI_PORT = 8081` but `app_fastapi.py` hardcodes port `8080` in its `__main__` block. The server actually runs on **8080**.
- The CI workflow's flake8 target (`rag_qa/`) does not exist in the repo; use `src/` instead.
