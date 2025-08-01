FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app
WORKDIR /app

COPY app/ /app
COPY pyproject.toml uv.lock /app/
RUN uv sync  

EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
CMD ["uv", "run", "python", "main.py"]
