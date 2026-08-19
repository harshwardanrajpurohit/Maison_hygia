# Maison Hygia — AI Ritual Concierge

Maison Hygia's AI Ritual Concierge is an intelligent, language-adaptive conversational agent designed to recommend personalized wellness and skincare rituals. It uses advanced intent extraction, information gain heuristics, and a conversational state machine to guide users from initial greeting to a fully customized ritual without relying on simple decision trees.

## Features

- **Multilingual Support**: Seamlessly handles English, Hindi, Marathi, and Hinglish. 
- **Conversational State Machine**: Robust tracking of modes (Greeting, Clarification, Recommendation, Safety) to prevent inappropriate context-jumping.
- **Safety First**: Implements an early medical guardrail to refuse diagnostic requests and offer general self-care instead.
- **Dynamic Prioritization**: Intelligently decides which questions to ask next (e.g., prioritizing Routine Time over Budget) based on information gain.
- **Relevance over Margin**: Ranks products primarily by consumer needs and preferences, not just business margins.

## Prerequisites

- **Python**: 3.9 or higher
- **Node.js** (Optional, if extending the frontend beyond simple HTTP server): Not strictly required for the Python FastAPI backend.
- **OpenAI API Key**: Required for the language, intent, and generation models.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/harshwardanrajpurohit/Margia_haigia.git
   cd Margia_haigia
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   Navigate to the `backend` directory and install the required packages.
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your OpenAI API Key:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

### 1. Command-Line Interface (CLI) Mode
To test the AI quickly in your terminal without spinning up a web server:
```bash
python demo_cli.py
```

### Running the Web Application
To run the full stack (FastAPI backend + Vanilla HTML/JS/CSS frontend), you only need to start the backend server because it is configured to serve the static frontend files directly:

```bash
python run.py
```
*The server will start on `http://localhost:8000`. Open this URL in your browser to interact with the concierge.*

## Project Structure

- `backend/`: Core logic
  - `engine/`: AI modules (intent, language, questions, recommender, generation, safety, vision)
  - `data/`: Product catalogs and knowledge chunks
  - `models.py`: Pydantic schemas for state, profile, and products
  - `conversation.py`: The main pipeline orchestrator
  - `main.py`: FastAPI endpoints
- `frontend/`: UI files (`index.html`, `app.js`, `styles.css`)
- `demo_cli.py`: Terminal testing script
- `run.py`: Backend server launcher
