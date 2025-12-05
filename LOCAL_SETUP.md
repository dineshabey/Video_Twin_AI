# 🚀 Local Development Guide

## Prerequisites
- Python 3.11+ installed
- Virtual environment activated (`.venv`)
- Google API Key

## Setup Steps

### 1. Install Dependencies
```powershell
.\.venv\Scripts\pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the `backend` folder:
```
GOOGLE_API_KEY=AIzaSyBoWbdLwTpNuhPul05xDEgNk86-ZT6UTZ4
```

### 3. Start the Backend Server
```powershell
.\.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
```

The backend will be available at: http://localhost:8000

### 4. Open the Frontend
Open `frontend/index.html` in your browser, OR use a simple HTTP server:

```powershell
# Option 1: Just double-click frontend/index.html

# Option 2: Use Python HTTP server (better for CORS)
cd frontend
python -m http.server 8080
```

Then open: http://localhost:8080

### 5. Update Frontend API URL (if needed)
If you're using the HTTP server, make sure `frontend/app.js` has:
```javascript
const API_URL = "http://localhost:8000";
```

## Testing Locally

1. **Paste a YouTube URL** (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)
2. **Click "Ingest Video"** - wait for "Video ingested!" message
3. **Ask a question** about the video
4. **Get AI response** based on the transcript

## Troubleshooting

### "Sign in to confirm you're not a bot" error
- Make sure `cookies.txt` exists in the project root
- Cookies should be fresh (exported recently)
- For local testing, cookies are optional if the video has public captions

### CORS errors
- Use the Python HTTP server instead of opening HTML directly
- Or disable CORS in your browser (for testing only)

### Port already in use
- Change port in the uvicorn command: `--port 8001`
- Update `API_URL` in `frontend/app.js` accordingly

## Development Workflow

1. **Backend changes**: Server auto-reloads (thanks to `--reload` flag)
2. **Frontend changes**: Just refresh the browser
3. **Check logs**: Terminal shows all backend logs and errors

## Stopping the Server
Press `Ctrl+C` in the terminal running uvicorn
