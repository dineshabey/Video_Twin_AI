const API_URL = "http://localhost:8000"; // For local development

const videoUrlInput = document.getElementById('video-url');
const ingestBtn = document.getElementById('ingest-btn');
const statusMessage = document.getElementById('status-message');
const chatSection = document.getElementById('chat-section');
const chatHistory = document.getElementById('chat-history');
const userQueryInput = document.getElementById('user-query');
const sendBtn = document.getElementById('send-btn');

ingestBtn.addEventListener('click', async () => {
    const url = videoUrlInput.value.trim();
    if (!url) return;

    ingestBtn.disabled = true;
    statusMessage.className = "";

    // Simulate progress steps
    const steps = [
        "Downloading subtitles...",
        "Chunking transcript...",
        "Generating embeddings...",
        "Storing in vector database..."
    ];

    let stepIndex = 0;
    statusMessage.textContent = steps[0];

    // Start a simulated progress interval
    const progressInterval = setInterval(() => {
        stepIndex++;
        if (stepIndex < steps.length) {
            statusMessage.textContent = steps[stepIndex];
        }
    }, 1500); // Change message every 1.5 seconds

    try {
        const response = await fetch(`${API_URL}/ingest`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        clearInterval(progressInterval); // Stop the simulated progress

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ingestion failed');
        }

        const data = await response.json();
        statusMessage.innerHTML = '<i class="fa-solid fa-circle-check" style="color: #10b981;"></i> Ingestion complete! Now you can chat with the video.';
        statusMessage.style.borderLeftColor = "#10b981"; // Green border
        chatSection.classList.remove('hidden');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            statusMessage.classList.add('hidden');
        }, 5000);

    } catch (error) {
        clearInterval(progressInterval);
        statusMessage.innerHTML = '<i class="fa-solid fa-circle-exclamation" style="color: #ef4444;"></i> Error: ' + error.message;
        statusMessage.style.borderLeftColor = "#ef4444"; // Red border
        ingestBtn.disabled = false;
    }
});

sendBtn.addEventListener('click', sendMessage);
userQueryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const query = userQueryInput.value.trim();
    if (!query) return;

    // Add user message to chat
    appendMessage(query, 'user');
    userQueryInput.value = '';
    sendBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: query })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Chat failed');
        }

        const data = await response.json();
        appendMessage(data.answer, 'ai');
        sendBtn.disabled = false;

    } catch (error) {
        appendMessage("Error: " + error.message, 'system');
        sendBtn.disabled = false;
    }
}



function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');

    if (sender === 'ai') {
        contentDiv.innerHTML = '<i class="fa-solid fa-robot" style="margin-right: 8px; color: var(--primary-color);"></i> ' + text;
    } else {
        contentDiv.textContent = text;
    }

    div.appendChild(contentDiv);

    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}
