# Learning-Focused Microservices E-Commerce App

This project demonstrates a simple microservices architecture using **Python (FastAPI)** and **Docker**. It includes 4 backend services and 1 frontend serving static files.

## 🏗️ Architecture (Refactored)

The system consists of the following services:

1.  **Frontend (Nginx)** (Port `8080`): The **single entry point**. Serves static files AND reverse-proxies API requests.
2.  **Gateway Service** (Internal): Receives requests from Frontend via Docker network.
3.  **User Service** (Internal): Manages user data.
4.  **Product Service** (Internal): Manages product data.
5.  **Order Service** (Internal): Handles orders.

### 🔒 Security Improvements

-   **Reverse Proxy**: The frontend uses Nginx to proxy connection to `/api/*` to the Gateway.
-   **No Exposed Backend Ports**: The backend services (8000-8003) are **NOT** exposed to the host machine. They live entirely inside the `microservices-net` Docker network. You can only access them via the Frontend.

### 🔌 Inter-Service Communication

-   **Browser -> Frontend (Port 8080)**:
    -   `GET /` -> Serves `index.html`.
    -   `GET /api/products` -> Proxied to `http://gateway-service:8000/products`.
-   **Gateway -> Microservices**: Routes internally.

## 🚀 How to Run

1.  **Create the `Dockerfile.backend`** in the root directory (`/Users/rosh/Learn/antigravity`) with the content provided below.
2.  **Create `microservices-app/frontend/Dockerfile`** and `nginx.conf` with the content provided.
3.  **Create `docker-compose.yml`** in the root directory.
4.  Run:
    ```bash
    docker-compose up --build
    ```
5.  Open your browser to: http://localhost:8080

### Dockerfile.backend
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### microservices-app/frontend/Dockerfile
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### microservices-app/frontend/nginx.conf
```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://gateway-service:8000;
        proxy_set_header Host $host;
    }
}
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  gateway-service:
    build:
      context: ./microservices-app/gateway_service
      dockerfile: ../../Dockerfile.backend
    container_name: gateway-service
    environment:
      - USER_SERVICE_URL=http://user-service:8000
      - PRODUCT_SERVICE_URL=http://product-service:8000
      - ORDER_SERVICE_URL=http://order-service:8000
    networks:
      - microservices-net
    depends_on:
      - user-service
      - product-service
      - order-service

  user-service:
    build:
      context: ./microservices-app/user_service
      dockerfile: ../../Dockerfile.backend
    container_name: user-service
    networks:
      - microservices-net

  product-service:
    build:
      context: ./microservices-app/product_service
      dockerfile: ../../Dockerfile.backend
    container_name: product-service
    networks:
      - microservices-net

  order-service:
    build:
      context: ./microservices-app/order_service
      dockerfile: ../../Dockerfile.backend
    container_name: order-service
    environment:
      - USER_SERVICE_URL=http://user-service:8000
      - PRODUCT_SERVICE_URL=http://product-service:8000
    networks:
      - microservices-net

  frontend:
    build:
      context: ./microservices-app/frontend
    container_name: frontend
    ports:
      - "8080:80"
    networks:
      - microservices-net

networks:
  microservices-net:
    driver: bridge
```
