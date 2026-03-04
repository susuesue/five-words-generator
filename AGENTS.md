# AGENTS.md

## Cursor Cloud specific instructions

This is a single-service Python FastAPI application ("五大需求提取器" / Five Needs Extractor) that calls the DeepSeek LLM API. No database, Docker, or frontend required.

### Running the service

- **Start server:** `python3 src/api/app_fastapi.py` (listens on port 8080, with hot-reload enabled)
- **Swagger docs:** `http://localhost:8080/docs`
- **Health check:** `GET http://localhost:8080/health`
- The `DEEPSEEK_API_KEY` environment variable is required for the `/extract` endpoints to return real results. Without it, the server starts fine but extraction returns empty fields (graceful degradation).
- Copy `.env.example` to `.env` and set your API key there; the app loads it via `python-dotenv`.

### Linting and testing

- **Lint:** `python3 -m flake8 src/ tests/ --max-line-length=120`
- **Test:** `python3 -m pytest tests/ -v` (15 tests covering extractor parsing, file handling, and API endpoints)
- Dev dependencies not in `requirements.txt`: `pytest`, `flake8`, `httpx`.
