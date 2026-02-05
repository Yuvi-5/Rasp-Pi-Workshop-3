import requests
import json
import os
import sys

# ==========================================
# 🎛️  CONTROL PANEL (EDIT THIS SECTION)
# ==========================================

# 1. THE BRAIN: Which AI model are we using?
MODEL_NAME = "llama3.2"  # Options: 'llama3.2', 'tinyllama', 'phi3'

# 2. THE KNOWLEDGE: What file should the AI read?
DATA_FILENAME = "ts.txt"  # Change this to your .txt file name

# 3. THE PERSONALITY: Who is the AI?
# Try changing this! Examples: "A grumpy pirate", "A helpful wizard", "A strict detective"
AI_SYSTEM_ROLE = "You are a Detective. Analyze the suspect's statement for inconsistencies."

# ==========================================
# 🛠️  SYSTEM SETTINGS (DO NOT EDIT)
# ==========================================
API_URL = "http://localhost:11434/api/generate"

# Terminal Colors for a "Pro" look
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def load_knowledge_base(filename):
    """Loads the text file into the program's memory."""
    if not os.path.exists(filename):
        print(f"{Colors.RED}❌ ERROR: Could not find the file '{filename}'{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Tip: Make sure your text file is in the same folder as this script!{Colors.RESET}")
        sys.exit(1) # Stop the program safely
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"{Colors.RED}❌ Error reading file: {e}{Colors.RESET}")
        sys.exit(1)

def query_local_ai(question, context):
    """Sends the package (Question + Context) to Ollama."""
    
    # This is the "Magic Trick" of RAG.
    # We combine the System Role, the Secret Data, and the Question into one big prompt.
    full_prompt = f"""
    [SYSTEM INSTRUCTION]
    {AI_SYSTEM_ROLE}

    [CONTEXT / KNOWLEDGE BASE]
    {context}

    [USER QUESTION]
    {question}
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status() # Check for HTTP errors
        return response.json()['response']
        
    except requests.exceptions.ConnectionError:
        return f"{Colors.RED}❌ ERROR: Is Ollama running? Try typing 'ollama serve' in a new terminal.{Colors.RESET}"

# ==========================================
# 🚀  MAIN PROGRAM EXECUTION
# ==========================================
if __name__ == "__main__":
    # Clear the screen for a fresh start
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f"{Colors.HEADER}{Colors.BOLD}╔══════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}║     🔒  LOCAL RAG SYSTEM: ONLINE         ║{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}╚══════════════════════════════════════════╝{Colors.RESET}")
    print(f" ► Model:   {Colors.GREEN}{MODEL_NAME}{Colors.RESET}")
    print(f" ► Source:  {Colors.BLUE}{DATA_FILENAME}{Colors.RESET}")
    print(f" ► Role:    {Colors.YELLOW}{AI_SYSTEM_ROLE}{Colors.RESET}")
    print("-" * 50)

    # 1. Load the data
    print("📂 Loading knowledge base...", end=" ")
    context_data = load_knowledge_base(DATA_FILENAME)
    print(f"{Colors.GREEN}Success!{Colors.RESET}")

    # 2. Start the Loop
    print(f"\n{Colors.BOLD}Type 'exit' to quit.{Colors.RESET}")
    
    while True:
        try:
            # Get User Input
            user_input = input(f"\n{Colors.BLUE}You (User):{Colors.RESET} ")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"\n{Colors.HEADER}👋 Shutting down RAG system. Goodbye!{Colors.RESET}")
                break
            
            if not user_input.strip():
                continue # Skip empty questions

            # Processing Animation
            print(f"{Colors.YELLOW}⚡ AI is thinking...{Colors.RESET}", end="", flush=True)

            # Get Answer
            answer = query_local_ai(user_input, context_data)
            
            # Print Answer (erase the "thinking" line first)
            print(f"\r{Colors.GREEN}🤖 AI ({MODEL_NAME}):{Colors.RESET} {answer}")

        except KeyboardInterrupt:
            print("\n\n👋 Forced exit detected. Goodbye!")
            break