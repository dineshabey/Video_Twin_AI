---
description: Deploy the Single-Video Twin API to Google Cloud Functions (Gen 2)
---

# Deploy to Google Cloud Functions

This workflow guides you through deploying the backend to Google Cloud Functions (2nd Gen).

## Prerequisites

1.  **Google Cloud Project**: You must have a Google Cloud project with billing enabled (Free Tier is available).
2.  **gcloud CLI**: Installed and authenticated (`gcloud auth login`).
3.  **APIs Enabled**: Enable the following APIs:
    *   Cloud Functions API
    *   Cloud Run API
    *   Artifact Registry API
    *   Cloud Build API

    ```bash
    gcloud services enable cloudfunctions.googleapis.com run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
    ```

    > **Note**: If you don't have `gcloud` installed, install it via winget:
    > ```bash
    > winget install Google.CloudSDK
    > ```
    > *After installation, restart your terminal.*

## Deployment Steps

1.  **Set your Project ID**:
    Replace `YOUR_PROJECT_ID` with your actual project ID.
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```

2.  **Deploy the Function**:
    Run the following command. Make sure to replace `YOUR_GOOGLE_API_KEY` with your actual Gemini API key.
    
    *   `--source=.`: Deploys the current directory.
    *   `--allow-unauthenticated`: Makes the API public.
    *   `--memory=1Gi`: 1GB memory.
    *   `--timeout=300`: 5 minutes timeout.

    ```bash
    gcloud run deploy single-video-twin \
    --source=. \
    --region=us-central1 \
    --allow-unauthenticated \
    --memory=1Gi \
    --timeout=300 \
    --set-env-vars GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
    ```

3.  **Get the URL**:
    After deployment, the command will output the `uri`. You can also find it with:
    ```bash
    gcloud functions describe single-video-twin --gen2 --region=us-central1 --format="value(serviceConfig.uri)"
    ```

## Important Limitations (Free Tier / Serverless)

*   **State Loss**: Cloud Functions are stateless. If the instance restarts or scales down, the **ingested video data (ChromaDB) will be lost**. You will need to re-ingest the video.
    *   *Mitigation*: For a robust solution, use a persistent vector database (e.g., Pinecone, Weaviate, or Chroma with persistent storage on GCS/Volume).
*   **Cold Starts**: The first request might take a few seconds to load.
*   **Concurrency**: By default, one instance handles multiple requests (Gen 2). However, global variables like `rag_service` are shared. This is fine for a single-user demo but not for multi-user production without session management.

## Testing

Once deployed, you can test it:

1.  **Ingest**:
    ```bash
    curl -X POST https://YOUR_FUNCTION_URL/ingest \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
    ```

2.  **Chat**:
    ```bash
    curl -X POST https://YOUR_FUNCTION_URL/chat \
    -H "Content-Type: application/json" \
    -d '{"question": "What is this video about?"}'
    ```

## Troubleshooting

### "gcloud is not recognized"
If you see this error, `gcloud` might be installed but not in your PATH.
Try running it with the full path:
```powershell
& "C:\Users\LENOVO\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" ...
```
Or add it to your PATH environment variable.
