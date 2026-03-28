FROM python:3.12-slim AS builder
WORKDIR /app
COPY packages/velora-common /app/packages/velora-common
COPY services/assessment /app/services/assessment
RUN pip install --no-cache-dir /app/packages/velora-common /app/services/assessment

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY services/assessment/src /app/src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
