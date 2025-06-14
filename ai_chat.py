import json
import os
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
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

# Main loop
print("🧠 AI with memory (Ctrl+C to exit)\n")
try:
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "bye", "Bye", "bye!", "Bye!"]:
            print("Saving conversation and exiting... 🐾")
            save_memory()
            break
        if user_input.lower() == "clear":
            memory.clear()
            print("Conversation history cleared! Starting fresh.")
            continue
        if not user_input:
            continue
        try:
            response = chain.invoke(user_input)
            memory.chat_memory.add_user_message(user_input)
            memory.chat_memory.add_ai_message(response)
            print(f"AI: {response}\n")
        except Exception as e:
            print(f"Error during conversation: {e}\n")
except KeyboardInterrupt:
    print("\nSaving conversation and exiting... 🐾")
    save_memory()
    print("Goodbye!")