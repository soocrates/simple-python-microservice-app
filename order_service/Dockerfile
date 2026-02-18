FROM python:3.14-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8083

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0"]

CMD ["--port", "8083"]

