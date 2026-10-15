FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN groupadd --system appuser \
    && useradd --system --gid appuser --create-home appuser

COPY --chown=appuser:appuser . /app/

RUN mkdir -p /app/staticfiles \
    && chown -R appuser:appuser /app/staticfiles

USER appuser

EXPOSE 8000

CMD ["gunicorn", "evu.wsgi:application", "--bind", "0.0.0.0:8000"]