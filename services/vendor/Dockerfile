FROM python:3.12-slim AS builder
WORKDIR /app
COPY packages/velora-common /app/packages/velora-common
COPY services/vendor /app/services/vendor
RUN pip install --no-cache-dir /app/packages/velora-common /app/services/vendor

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY services/vendor/src /app/src
RUN useradd -r -u 1001 appuser && chown -R appuser /app
USER appuser
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
