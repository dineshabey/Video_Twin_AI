# Single-Video Twin AI 🎥🤖

A full-stack AI application that transforms any YouTube video into an intelligent conversational agent. Ask questions about the video content and get accurate answers based on the transcript.

## 🎯 Features

- **YouTube Video Ingestion**: Simply paste a YouTube URL
- **RAG Pipeline**: Retrieval-Augmented Generation for accurate answers
- **Context-Aware Responses**: AI answers strictly based on video content
- **Modern UI**: Clean, responsive interface
- **Cloud Deployed**: Production-ready on Google Cloud Run

## 🚀 Live Demo

**Deployed URL**: [https://single-video-twin-298684878814.us-central1.run.app/](https://single-video-twin-298684878814.us-central1.run.app/)

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- Responsive design with modern UI/UX

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: 
  - LangChain for RAG pipeline
  - Google Gemini 2.0 Flash (LLM)
  - Google text-embedding-004 (Embeddings)
- **Vector Store**: ChromaDB (in-memory)
- **Video Processing**: yt-dlp for transcript extraction

### Cloud Infrastructure
- **Platform**: Google Cloud Run (Serverless)
- **Deployment**: Automated via gcloud CLI
- **Environment**: Production-ready with environment variables

## 📋 Prerequisites

- Python 3.11+
- Google Cloud Account (for deployment)
- Google API Key (for Gemini AI)

## 🔧 Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/dineshabey/Video_Twin_AI.git
cd chat-with-youtube-video
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create a `.env` file in the `backend` folder:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 5. Get YouTube Cookies (Optional but Recommended)
For better reliability, export your YouTube cookies:
1. Install "Get cookies.txt LOCALLY" browser extension
2. Go to youtube.com and log in
3. Export cookies and save as `cookies.txt` in project root

### 6. Start Backend Server
```bash
uvicorn backend.main:app --reload --port 8000
```

### 7. Start Frontend Server
Open a **new terminal** (keep backend running):
```bash
cd frontend
python -m http.server 8080
```

### 8. Access the Application
**IMPORTANT:** Open your browser and navigate to:
```
http://localhost:8080
```

⚠️ **Common Mistake:** Do NOT use `http://localhost:8000`
- ✅ `http://localhost:8080` - Frontend server (CSS/JS work correctly)
- ❌ `http://localhost:8000` - Backend API only (CSS/JS will not load)

**Why?** The backend (port 8000) serves the API, while the frontend server (port 8080) serves the UI with proper static file paths.

## 🎬 How to Use

1. **Paste YouTube URL**: Enter any YouTube video URL with captions
2. **Click "Ingest Video"**: Wait for the transcript to be processed
3. **Ask Questions**: Type your question about the video content
4. **Get AI Answers**: Receive context-aware responses based on the transcript

### Example Videos to Try:
- Tech tutorials
- Educational content
- Interviews
- Podcasts
- Any video with captions/subtitles

## 🌐 Cloud Deployment

### Deploy to Google Cloud Run

1. **Install Google Cloud SDK**
```bash
# Windows
winget install Google.CloudSDK

# Or download from: https://cloud.google.com/sdk/docs/install
```

2. **Authenticate**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Deploy**
```bash
gcloud run deploy single-video-twin \
  --source=. \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=300 \
  --set-env-vars GOOGLE_API_KEY=your_api_key_here
```

4. **Update Cookies (if needed)**
```bash
# Encode cookies to base64
$base64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content cookies.txt -Raw)))

# Update environment variable
gcloud run services update single-video-twin \
  --region=us-central1 \
  --update-env-vars="YOUTUBE_COOKIES_BASE64=$base64"
```

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py       # API routes
│   │   └── services/
│   │       ├── ingestion.py       # YouTube transcript extraction
│   │       ├── rag_service.py     # RAG pipeline logic
│   │       ├── vector_store.py    # ChromaDB management
│   │       └── youtube_service.py # YouTube utilities
│   ├── main.py                    # FastAPI app entry point
│   └── requirements.txt           # Backend dependencies
├── frontend/
│   ├── index.html                 # Main UI
│   ├── style.css                  # Styling
│   └── app.js                     # Frontend logic
├── requirements.txt               # Root dependencies
├── Procfile                       # Cloud Run configuration
├── .gcloudignore                  # Files to exclude from deployment
└── README.md                      # This file
```

## 🔍 How It Works

### RAG Pipeline

1. **Ingestion**:
   - User provides YouTube URL
   - `yt-dlp` extracts video transcript
   - Text is split into chunks (1000 chars, 200 overlap)

2. **Embedding**:
   - Chunks are embedded using Google's `text-embedding-004`
   - Embeddings stored in ChromaDB vector store
   - Rate limiting and retry logic for API stability

3. **Retrieval**:
   - User question is embedded
   - Similarity search finds relevant chunks
   - Top results passed as context to LLM

4. **Generation**:
   - Google Gemini 2.0 Flash generates answer
   - System prompt ensures answers use only provided context
   - Response returned to user

## 🐛 Troubleshooting

### "Sign in to confirm you're not a bot" Error
- Export fresh YouTube cookies
- Update `YOUTUBE_COOKIES_BASE64` environment variable
- Cookies expire after a few weeks/months

### CORS Errors (Local Development)
- Use Python HTTP server instead of opening HTML directly
- Ensure backend is running on port 8000
- Check `API_URL` in `frontend/app.js`

### CSS/JavaScript Not Loading Locally
**Problem:** Page loads but has no styling (plain HTML)

**Solution:** Make sure you're accessing the **frontend server**, not the backend:
- ✅ Correct: `http://localhost:8080`
- ❌ Wrong: `http://localhost:8000` or `http://127.0.0.1:8000`

**Why?** The backend server expects `/static/` prefix for CSS/JS files, but the HTML uses relative paths. The frontend server (port 8080) serves files correctly.

### Port Already in Use
```bash
# Change backend port
uvicorn backend.main:app --reload --port 8001

# Update API_URL in frontend/app.js accordingly
```

### No Subtitles Found
- Ensure the video has captions/subtitles enabled
- Try a different video with auto-generated captions
- Check if video is region-restricted

## 📊 API Endpoints

### `POST /ingest`
Ingest a YouTube video transcript
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

### `POST /chat`
Ask a question about the ingested video
```json
{
  "query": "What is the main topic of the video?"
}
```

### `GET /health`
Health check endpoint
```json
{
  "status": "healthy"
}
```

## ⚠️ Limitations

- **Single Video**: Only one video can be active at a time (in-memory storage)
- **Ephemeral Storage**: Data is lost when Cloud Run instance restarts
- **Cookie Expiration**: YouTube cookies need periodic refresh
- **Free Tier Limits**: Google AI API has rate limits on free tier

## 🚀 Future Enhancements

- [ ] Multi-user support with session management
- [ ] Persistent vector database (Pinecone/Weaviate)
- [ ] Support for multiple videos per user
- [ ] Video timestamp references in answers
- [ ] Support for playlists
- [ ] Custom domain and branding

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, LangChain, and Google Gemini AI**
