FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app

# Run-time python differs per environment: after `uv sync` (Glama's build spec)
# packages live in /app/.venv; after `pip install .` (plain docker build) they
# live in the system python site-packages. Prefer the venv when present.
CMD ["sh", "-c", "if [ -x .venv/bin/python ]; then exec .venv/bin/python -m quality_coach_mcp.server; else exec python -m quality_coach_mcp.server; fi"]
