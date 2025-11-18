# ATLAS Containerization & Deployment Guide

## Overview

Your ATLAS application has been containerized to support deployment on Render and other container platforms. The setup includes:

- **Python Application**: Google ADK agent with email, calendar, search, and memory tools
- **Node.js Service**: Google Calendar MCP server
- **Multi-stage Docker Build**: Optimized image with minimal footprint
- **Docker Compose**: Local development setup
- **Render Configuration**: Production deployment ready

## Files Created

### Docker Files
- **`Dockerfile`** - Multi-stage build for Python + Node.js application
- **`.dockerignore`** - Excludes unnecessary files from image
- **`docker-compose.yml`** - Development environment orchestration
- **`entrypoint.sh`** - Startup script for both services

### Configuration Files
- **`requirements.txt`** - Python dependencies
- **`render.yaml`** - Render deployment configuration
- **`.env.production`** - Production environment template

## Local Development with Docker

### Prerequisites
- Docker and Docker Compose installed
- Google API credentials (credentials.json)
- Environment variables configured

### Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the application
docker-compose up

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Environment Setup for Local Development

1. Create a `.env` file in `ATLAS/` directory:
```bash
GOOGLE_API_KEY=your_key_here
GOOGLE_SEARCH_API_KEY=your_search_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

2. Ensure you have Google credentials:
```bash
# Credentials should be at:
ATLAS/credentials/calendar_token.json
ATLAS/credentials/gmail_token.json
```

## Deployment on Render

### Step 1: Prepare Repository

Ensure all files are committed to GitHub:
```bash
git add Dockerfile docker-compose.yml requirements.txt entrypoint.sh .dockerignore render.yaml .env.production
git commit -m "Add Docker containerization and Render deployment configuration"
git push
```

### Step 2: Create Render Service

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select the `master` branch
5. Configure the service:
   - **Name**: `atlas-app` (or your preferred name)
   - **Environment**: Docker
   - **Instance Type**: Standard (or as needed)
   - **Auto Deploy**: Enable if desired

### Step 3: Set Environment Variables

In Render dashboard, go to your service's **Environment** section and add:

```
GOOGLE_API_KEY=your_api_key_here
GOOGLE_SEARCH_API_KEY=your_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
GOOGLE_GENAI_USE_VERTEXAI=0
PYTHONUNBUFFERED=1
```

### Step 4: Configure Credentials (Important!)

For production, you need to handle credentials securely:

**Option A: Use Environment-based Credentials (Recommended)**
1. Store your `gcp-oauth.keys.json` content as a Render Secret:
   - Go to **Environment** in Render dashboard
   - Add a variable: `GCP_OAUTH_CREDENTIALS` (as file or base64)

**Option B: Mount Secret Files**
- Use Render's disk feature to persist credentials between deployments

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically detect `render.yaml` and `Dockerfile`
3. The service will build and deploy automatically
4. Check logs in Render dashboard for deployment status

## Docker Image Structure

### Multi-stage Build Optimization

**Stage 1 (node-builder)**
- Builds Google Calendar MCP Node.js server
- Installs only production dependencies

**Stage 2 (Final)**
- Python 3.11 slim image base
- Includes Node.js 18 runtime
- Copies pre-built Node.js app
- Installs Python dependencies
- Non-root user for security
- Health checks configured

### Image Size Optimization
- Multi-stage build reduces final image size
- Production dependencies only (no dev tools)
- Alpine-based Node image for smaller footprint
- Slim Python image

## Running Modes

### Development Mode (Local)

```bash
docker-compose up --build
```

- Source code can be volume-mounted for live changes
- Full logging output visible
- All debugging tools available

### Production Mode (Render)

- Optimized image with production dependencies
- Non-root user execution
- Health checks enabled
- Automatic restarts on failure
- Environment-based configuration

## Managing Credentials

### Local Development
- Store in `ATLAS/credentials/` directory
- Include in `.env` file
- Use `.gitignore` to exclude from version control

### Render Production
1. **Use Render Secrets** for sensitive data:
   ```bash
   GOOGLE_API_KEY=secret_key_value
   ```

2. **Store OAuth credentials** in Render disk:
   - Mount persistent disk at `/app/data`
   - Use initialization script to load credentials

3. **Avoid committing secrets** to Git:
   - Use `.env.production` as template only
   - Never commit actual credentials

## Troubleshooting

### Build Issues

**Node modules not found:**
```bash
# Ensure package-lock.json is committed
git add ATLAS/google-calendar-mcp/package-lock.json
```

**Python dependencies not installing:**
```bash
# Check requirements.txt is in root directory
ls requirements.txt
```

### Runtime Issues

**Calendar MCP not starting:**
- Check `GOOGLE_OAUTH_CREDENTIALS` path
- Ensure `gcp-oauth.keys.json` is accessible

**Python agent not connecting to MCP:**
- Verify MCP starts before Python agent (handled in entrypoint.sh)
- Check port 3000 is available

**Credentials not loading:**
- Verify environment variables are set correctly
- Check file permissions (non-root user access)

### Render-Specific Issues

**Service won't start:**
1. Check Build Logs in Render dashboard
2. Verify all environment variables are set
3. Ensure Dockerfile path is correct (`./Dockerfile`)

**Credentials/Permissions errors:**
1. Re-check environment variable names
2. Ensure secrets are properly escaped
3. Check user permissions (atlas user)

## Port Configuration

- **Default**: 3000 (Calendar MCP HTTP server)
- **Render**: Automatically maps to HTTPS on your Render domain
- **Custom**: Modify `EXPOSE` in Dockerfile or environment variable `PORT`

## Monitoring & Logs

### Local Development
```bash
docker-compose logs -f atlas
docker-compose logs -f --tail=100  # Last 100 lines
```

### Render Dashboard
1. Go to your service page
2. Click "Logs" tab
3. View real-time logs
4. Filter by date/time range

## Updating Deployment

### Deploy Code Changes

```bash
git add .
git commit -m "Update ATLAS code"
git push
```

Render will automatically rebuild and redeploy (if Auto Deploy is enabled).

### Update Dependencies

1. Update `requirements.txt` or `package.json`
2. Commit changes
3. Push to GitHub
4. Render will rebuild with new dependencies

### Rollback

Render keeps build history. To rollback:
1. Go to **Deploys** in Render dashboard
2. Click "Redeploy" on a previous deployment
3. Service will revert to that version

## Performance Considerations

- **Memory**: Start with Render's default allocation
- **CPU**: Standard instance sufficient for single-user application
- **Build Time**: First build ~5-10 minutes (subsequent builds cached)
- **Cold Starts**: Service may take 30-60 seconds to start from sleep

## Security Best Practices

✅ **Implemented**
- Non-root user execution
- Secrets in environment variables
- .dockerignore for sensitive files
- Health checks enabled

✅ **Recommended**
- Enable HTTPS (Render provides free SSL)
- Rotate credentials regularly
- Use Render's private networking if available
- Monitor logs for suspicious activity

## Next Steps

1. **Test locally**: `docker-compose up`
2. **Push to GitHub**: Ensure all files are committed
3. **Create Render service**: Follow "Deployment on Render" steps
4. **Set environment variables**: Add all required API keys
5. **Monitor deployment**: Check logs for any errors

## Support

For issues:
1. Check Render logs: Dashboard → Logs tab
2. Review Docker build output: Build fails → Show build logs
3. Test locally first: `docker-compose up`
4. Verify environment variables: Check Render Environment tab

---

**Last Updated**: November 18, 2025
**ATLAS Version**: 2.0
**Docker Base**: Python 3.11 + Node.js 18
**Platform**: Render (Container Runtime)
