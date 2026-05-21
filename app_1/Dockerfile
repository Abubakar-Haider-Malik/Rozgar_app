# ---- Stage 1: Build Frontend ----
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies first for caching
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Copy frontend source and build Next.js (generates static files in /app/frontend/out)
COPY frontend ./frontend
RUN cd frontend && npm run build

# ---- Stage 2: Runtime Backend ----
FROM python:3.11-slim

WORKDIR /app

# Install python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend ./backend

# Copy built frontend assets from the builder stage
COPY --from=builder /app/frontend/out ./frontend/out

# Ensure the root requirements.txt is copied if required by Cloud Run, 
# but Docker handles everything via the image.
ENV PORT=8080
EXPOSE 8080

# Start FastAPI using uvicorn
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
