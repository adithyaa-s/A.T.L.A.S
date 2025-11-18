# Quick Start: ATLAS Docker & Render Deployment

## 📦 What Was Created

Your application has been containerized! Here's what's new:

### Docker Files
- ✅ `Dockerfile` - Builds your app with Python + Node.js
- ✅ `.dockerignore` - Excludes unnecessary files
- ✅ `docker-compose.yml` - Local development setup
- ✅ `entrypoint.sh` - Startup script
- ✅ `requirements.txt` - Python dependencies

### Configuration Files
- ✅ `render.yaml` - Render deployment config
- ✅ `.env.production` - Production environment template
- ✅ `DEPLOYMENT.md` - Comprehensive deployment guide

## 🚀 Quick Start (Local)

### 1. Build and Run Locally

```bash
# From project root
docker-compose up --build
```

That's it! Your app will start at `localhost:3000`

### 2. Stop

```bash
docker-compose down
```

## 🌐 Deploy to Render

### 1. Commit Everything

```bash
cd /home/adithyaa/Projects/ATLAS
git add .
git commit -m "Add Docker containerization for Render"
git push
```

### 2. Go to Render

1. Visit [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Select your repo
5. Render will auto-detect `render.yaml` and `Dockerfile`

### 3. Set Environment Variables

In Render dashboard → Environment, add:

```
GOOGLE_API_KEY=your_api_key
GOOGLE_SEARCH_API_KEY=your_search_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

### 4. Deploy

Click "Create Web Service" - done! 🎉

Your app will be live in ~5-10 minutes at your Render URL.

## 📋 File Structure

```
ATLAS/
├── Dockerfile              ← Multi-stage build
├── .dockerignore          ← Files to exclude
├── docker-compose.yml     ← Local development
├── entrypoint.sh          ← Startup script
├── requirements.txt       ← Python deps
├── render.yaml            ← Render config
├── .env.production        ← Production env template
├── DEPLOYMENT.md          ← Full deployment guide (READ THIS!)
├── agent.py               ← Your Python agent
├── google-calendar-mcp/   ← Your Node.js MCP server
├── tools/                 ← Python tools
└── credentials/           ← Your API credentials
```

## 🔑 Important Notes

### Credentials
- **Local**: Keep `ATLAS/credentials/` folder with token files
- **Render**: Set API keys as environment variables in dashboard
- Never commit actual credentials - use `.env.production` as template

### What Happens
1. Dockerfile builds Node.js Calendar MCP server
2. Installs Python dependencies
3. `entrypoint.sh` starts both services
4. Python agent connects to MCP server
5. Your app runs! 🎉

### Ports
- **3000**: Calendar MCP HTTP server (exposed to Render)

## 🐛 Troubleshooting

### Docker build fails?
```bash
# Check requirements.txt exists
ls requirements.txt

# Check Dockerfile is valid
docker build -t atlas-test .
```

### App won't start locally?
```bash
# Check compose setup
docker-compose ps

# View logs
docker-compose logs -f
```

### Render deployment fails?
1. Check "Build Logs" in Render dashboard
2. Ensure all env vars are set
3. Check errors in "Logs" tab
4. See DEPLOYMENT.md for troubleshooting

## 📚 Next Steps

1. **Test locally first**: `docker-compose up`
2. **Read full guide**: Check `DEPLOYMENT.md` for details
3. **Deploy to Render**: Follow "Deploy to Render" above
4. **Monitor**: Check Render logs after deployment

## 🎯 Quick Commands

```bash
# Build locally
docker build -t atlas .

# Run container manually
docker run -e GOOGLE_API_KEY=xxx atlas

# Build with compose
docker-compose build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up --build
```

---

**Everything is ready!** Follow the steps above to deploy to Render. 🚀
