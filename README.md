🧠 Workshop 3: Edge Intelligence & Local AI

From Distributed Sensor Grids to Private RAG Systems

Brought to you by: Circuit Revival

Delivered by: Yuvraj

📖 Overview

Welcome to Workshop 3! In this session, we bridge the gap between the physical world (IoT) and cognitive intelligence (Generative AI). You will build a full-stack Edge AI system that not only senses its environment but can also reason about data using private, local Large Language Models (LLMs).

🎯 Learning Objectives

The Body (IoT): Master GPIO basics, digital/analog sensors, and real-time telemetry streaming using Python and SocketIO.

The Brain (GenAI): Deploy local LLMs (Llama 3.2, Phi-3) on a Raspberry Pi using Ollama.

The Bridge (RAG): Build a Retrieval Augmented Generation (RAG) system to allow AI to answer questions based on private data (medical records, mission logs, etc.) without internet access.

🛠️ Hardware Requirements

Raspberry Pi 4 Model B or Raspberry Pi 5 (8GB RAM recommended for AI).

Grove Base Hat for Raspberry Pi.

Sensors:

Grove Moisture Sensor (Analog).

Grove Light Sensor v1.2 (Analog).

Grove DHT11 Temperature & Humidity Sensor (Digital).

Actuators:

LED (Digital).

Buzzer (Digital).

LCD Display (I2C - Optional).

📂 Repository Structure

📦 Rasp-Pi-Workshop-3

📂 InitialCodes/ (Sandbox scripts to test individual sensors)

    📜 light.py - Test Light Sensor (Port A2)

    📜 moist.py - Test Moisture Sensor (Port A0)

    📜 th.py - Test DHT11 Sensor (Port D5)

📂 EdgeNode/ (PHASE 1: The IoT Logic)
  
    📜 edge_node.py - Main script for sensor data & telemetry
  
📂 Rag/ (PHASE 2: The Local AI Brain)

    📜 rag.py - The RAG engine (connects to Ollama)

    📜 mission_logs.txt - Sample dataset (Sci-Fi context)

    📜 patient_data.txt - Sample dataset (Medical context)

    📜 ... - Other sample data files

📂 extra/ (Instructor solutions & reference code)

    📜 solution_node.py


⚙️ Setup & Installation

1. Install Python Dependencies

Run the following command to install the necessary libraries for hardware control and networking:

pip install grove.py psutil socketio requests


Note: If you are using a virtual environment, ensure it is activated.

2. Install Ollama (For Phase 2)

We use Ollama to run LLMs locally on the Pi.

curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh


3. Pull the AI Models

Download the models we will use (Warning: These are large files, ~2GB+):

ollama pull llama3.1  # The "Smart" model
ollama pull tinyllama # The "Fast" model


🚀 Phase 1: The Body (Sensors & Telemetry)

Time: 18:00 - 19:20

In this phase, we build the nervous system. We will read data from the physical world and stream it to a central dashboard.

Step 1: Test Your Sensors

Before running the main code, verify your wiring using the scripts in InitialCodes/.

Moisture: Connect to A0 -> Run python InitialCodes/moist.py

Light: Connect to A2 -> Run python InitialCodes/light.py

Temp/Humid: Connect to D5 -> Run python InitialCodes/th.py

Step 2: Configure the Edge Node

Open EdgeNode/edge_node.py and edit the Hardware Configuration section:

# --- SERVER SETTINGS ---
SERVER_IP = '[http://192.168.137.1:5000](http://192.168.137.1:5000)'  # Update this from the whiteboard
TEAM_NAME = 'Team Alpha'                  # Give your node a unique name

# --- SENSORS ---
MOISTURE_PORT = 0     # Set to 0 if connected to A0
LIGHT_PORT    = 2     # Set to 2 if connected to A2
DHT_PORT      = 5     # Set to 5 if connected to D5


Step 3: Run the Telemetry Stream

python EdgeNode/edge_node.py


If successful, you will see:

📡 Connecting to Dashboard...
🟢 ONLINE. Streaming Data...

🧠 Phase 2: The Brain (Local RAG)

Time: 19:40 - 21:00

In this phase, we turn the Pi into a private intelligence server. It will read a secret text file and answer questions about it using Generative AI.

Step 1: Configure the RAG Engine

Open Rag/rag.py and modify the Control Panel:

# 1. Choose your Brain
MODEL_NAME = "llama3.1" 

# 2. Choose your Knowledge Base
DATA_FILENAME = "mission_logs.txt" 

# 3. Choose the Persona
AI_SYSTEM_ROLE = "You are a Commander. Brief the team on the status."


Step 2: Launch the AI

Ensure the Ollama service is running in the background, then run:

python Rag/rag.py


Step 3: Interrogate the Data

Try asking questions based on the file you loaded.

If loaded mission_logs.txt: "What is the new escape code?"

If loaded patient_data.txt: "What is Sarah allergic to?"

If loaded suspect_file.txt: "Where did the suspect say he was?"

The AI will retrieve the specific line from the text file and generate a natural language response.

⚠️ Troubleshooting

ImportError: No module named 'grove': You missed the installation step. Run pip install grove.py.

Connection Refused (Edge Node): Check that the SERVER_IP in edge_node.py matches the instructor's screen exactly. Ensure you are on the correct Wi-Fi.

Ollama Connection Error: Ensure Ollama is running (systemctl status ollama). If not, open a new terminal and type ollama serve.

Sensor reads 0/NaN: Check your wiring. Ensure Analog sensors are in A ports and Digital sensors are in D ports.

📜 Credits

Instructor: Yuvraj Singh Palh

Tech Stack: Raspberry Pi, Python, Ollama, Flask, SocketIO
