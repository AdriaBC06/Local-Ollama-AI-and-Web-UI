import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# System instructions
# CHANGE THIS TO CHANGE THE INITAL PROMPT
SYSTEM_INSTRUCTIONS = "You are an AI assistant, designed to reply to prompts by the user"

# File to store persistent memory
MEMORY_FILE = "conversation_memory.json"

# Initialize the AI model via Ollama
# CHANGE THOS TO CHANGE THE OLLAMA MODEL
try:
    llm = ChatOllama(model="ai-model")
except Exception as e:
    print(f"Error initializing model: {e}")
    print("Ensure Ollama is running and 'ai-model' is installed (check with 'ollama list').")
    exit(1)

# Initialize memory
memory = ConversationBufferMemory(return_messages=True)

# Load memory from file if it exists
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
                for entry in data:
                    if entry["type"] == "human":
                        memory.chat_memory.add_user_message(entry["content"])
                    elif entry["type"] == "ai":
                        memory.chat_memory.add_ai_message(entry["content"])
            print("Loaded previous conversation from file.")
        except Exception as e:
            print(f"Error loading memory: {e}")

# Save memory to file
def save_memory():
    try:
        messages = []
        for msg in memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                messages.append({"type": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"type": "ai", "content": msg.content})
        with open(MEMORY_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
        print("Conversation saved to file.")
    except Exception as e:
        print(f"Error saving memory: {e}")

# Load existing memory
load_memory()

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_INSTRUCTIONS),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# Create a custom chain
chain = (
    {
        "history": lambda x: memory.load_memory_variables({})["history"],
        "input": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# Global flag to signal server shutdown
shutdown_server = False

# HTTP Server Handler
class ChatHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global shutdown_server
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)
        user_input = params.get('message', [''])[0]

        if user_input.lower() in ["exit", "quit", "bye"]:
            save_memory()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": "Conversation saved. Goodbye! 🐾", "shutdown": True}).encode())
            shutdown_server = True  # Set flag to stop server
            return

        if user_input.lower() == "clear":
            memory.clear()
            save_memory()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": "Conversation history cleared! Starting fresh."}).encode())
            return

        try:
            response = chain.invoke(user_input)
            memory.chat_memory.add_user_message(user_input)
            memory.chat_memory.add_ai_message(response)
            save_memory()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": f"Error: {str(e)}"}).encode())

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            file_path = "index.html"
            content_type = "text/html"
        else:
            file_path = self.path.strip("/")
            if not os.path.isfile(file_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found.")
                return
            # Establecer tipo MIME
            if file_path.endswith(".css"):
                content_type = "text/css"
            elif file_path.endswith(".js"):
                content_type = "application/javascript"
            elif file_path.endswith(".png"):
                content_type = "image/png"
            elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                content_type = "image/jpeg"
            else:
                content_type = "application/octet-stream"

        try:
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error reading file: {str(e)}".encode())


# Run the server
def run_server():
    global shutdown_server
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, ChatHandler)
    print("Starting server on http://localhost:8000")
    try:
        while not shutdown_server:
            httpd.handle_request()  # Handle one request at a time
        print("\nSaving conversation and shutting down... 🐾")
        save_memory()
        httpd.server_close()
    except KeyboardInterrupt:
        print("\nSaving conversation and shutting down... 🐾")
        save_memory()
        httpd.server_close()

if __name__ == "__main__":
    run_server()