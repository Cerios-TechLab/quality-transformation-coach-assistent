FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app

CMD ["python", "-m", "quality_coach_mcp.server"]