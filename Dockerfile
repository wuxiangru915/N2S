# Build stage: compile the N2S web component bundle
FROM node:22-alpine AS frontend
WORKDIR /app/frontend
COPY frontends/webcomponent/package.json ./
RUN npm install --ignore-scripts && node node_modules/esbuild/install.js
COPY frontends/webcomponent/ ./
RUN node scripts/sync-version.js \
    && ./node_modules/.bin/tsc \
    && ./node_modules/.bin/vite build

# Runtime stage: Python backend with built frontend
FROM python:3.11-slim
WORKDIR /app

COPY pyproject.toml README.md NOTICE LICENSE ./
COPY src ./src
COPY --from=frontend /app/frontend/dist ./frontends/webcomponent/dist

RUN pip install --no-cache-dir -e ".[fastapi]"

EXPOSE 8000

CMD ["python", "-m", "n2s.demo"]
