# Stage 1: builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim
RUN useradd -m -u 1000 vigil
WORKDIR /app
COPY --from=builder /root/.local /home/vigil/.local
COPY . .
RUN chown -R vigil:vigil /app
USER vigil
ENV PATH=/home/vigil/.local/bin:$PATH
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
