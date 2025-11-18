# Multi-stage Dockerfile for ATLAS - Python + Node.js application
# syntax=docker/dockerfile:1

# Stage 1: Build Node.js components (Google Calendar MCP)
FROM node:18-alpine as node-builder

WORKDIR /app/google-calendar-mcp

# Copy package files
COPY ATLAS/google-calendar-mcp/package*.json ./

# Copy source files needed for build
COPY ATLAS/google-calendar-mcp/scripts ./scripts
COPY ATLAS/google-calendar-mcp/src ./src
COPY ATLAS/google-calendar-mcp/tsconfig.json ./
COPY ATLAS/google-calendar-mcp/tsconfig.lint.json ./
COPY ATLAS/google-calendar-mcp/vitest.config.ts ./

# Install and build
RUN npm ci --no-audit --no-fund --silent && \
    npm run build && \
    npm prune --production --silent


# Stage 2: Final runtime image
FROM python:3.11-slim

# Install Node.js runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r atlas && useradd -r -g atlas atlas

WORKDIR /app

# Copy Python application files
COPY ATLAS/ ./ATLAS/

# Copy built Node.js application from builder
COPY --from=node-builder /app/google-calendar-mcp/build ./ATLAS/google-calendar-mcp/build
COPY --from=node-builder /app/google-calendar-mcp/node_modules ./ATLAS/google-calendar-mcp/node_modules

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create credentials and config directories
RUN mkdir -p /app/ATLAS/credentials /app/config && \
    chown -R atlas:atlas /app

# Switch to non-root user
USER atlas

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/ATLAS/google-calendar-mcp/node_modules/.bin:$PATH"

# Copy entry point script
COPY --chown=atlas:atlas ATLAS/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Expose port for HTTP server (optional)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "print('OK')" || exit 1

# Run application
CMD ["/app/entrypoint.sh"]
