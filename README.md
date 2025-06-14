# Web Interface for Local AI Interaction

This project allows you to interact with a local AI language model through a simple web-based menu.

## Requirements

Make sure you have the following installed:

- Ollama (to run local language models)

- Python 3.8 or higher

- pip (Python package manager)

## Installation

1. Clone this repository:
   ```
    git clone https://github.com/AdriaBC06/Local-Ollama-AI-Web-UI.git
    cd Local-Ollama-AI-Web-UI
   ```
2. (Optional) Activate a virtual environment:
   ```
    source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install the Python dependencies:
   ```
    pip install -r requirements.txt
   ```

## Usage
### Option 1: Run the web interface
To start the local web server:
    ```
    python ai_chat_web.py
    ```
This will open a local server (at `http://localhost:8000`) with a menu to interact with the AI, using `index.html` and `styles.css` for the interface.

### Option 2: Run in the terminal
If you prefer using the AI directly from the terminal:
    ```
    python ai_chat.py
    ```

## Configuration

You __must__ configure the model name or other settings directly in `ai_chat.py` or `ai_chat_web.py`.

## Project Structure
    .
    ├── conversation_memory.json  # Stores chat history
    ├── index.html               # HTML template for the web interface
    ├── styles.css               # CSS styles for the web interface
    ├── venv/                    # Python virtual environment
    ├── vicuna_chat.py           # CLI version for terminal interaction
    ├── vicuna_chat_web.py       # Starts the web interface
    ├── requirements.txt         # Python dependencies
