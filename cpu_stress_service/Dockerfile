FROM python:3.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY . .
EXPOSE 8084
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8084"]