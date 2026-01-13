# Stage 1: Build the Next.js static files
FROM node:22-alpine AS frontend-builder
WORKDIR /app

# Copy package files first
# Changed to 'npm install' to handle missing package-lock.json
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy all frontend files
COPY . .

# Build argument for Clerk public key (baked into the static JS)
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

# Build the Next.js app (creates the 'out' directory)
RUN npm run build

# Stage 2: Create the final Python container
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI server code from your api folder
COPY api/server.py .

# Copy the static 'out' folder from the builder stage into 'static'
COPY --from=frontend-builder /app/out ./static

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]