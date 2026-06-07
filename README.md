# 🏥 HealthMate AI

An AI-powered healthcare assistant that helps users analyze symptoms, predict possible diseases, track health metrics, receive diet recommendations, and interact with an intelligent medical chatbot.

---

## 🚀 Features

### 💬 AI Healthcare Chatbot
- Natural language conversation
- Medical question answering
- Context-aware responses
- Symptom discussion and guidance

<img width="1470" height="798" alt="image" src="https://github.com/user-attachments/assets/ded7fa51-b408-407c-99e0-65abf308e34e" />


### 🔍 Disease Prediction
- Predicts possible diseases from symptoms
- Machine Learning-based diagnosis
- Severity assessment for symptoms

<img width="1470" height="798" alt="image" src="https://github.com/user-attachments/assets/6f0c920c-d3e6-4d5a-840d-d464a534c172" />


### 📊 Health Dashboard
- BMI Calculator
- Daily health monitoring
- Personalized health insights
- Interactive visualizations

<img width="1470" height="798" alt="image" src="https://github.com/user-attachments/assets/44f21e69-fce7-4282-a888-95ca2bc231b3" />


### 🥗 Diet & Nutrition Guidance
- Personalized diet suggestions
- BMI-based recommendations
- Healthy lifestyle guidance

<img width="1470" height="798" alt="image" src="https://github.com/user-attachments/assets/509cb6a2-256c-45a7-947f-10437812f358" />
<img width="1155" height="342" alt="image" src="https://github.com/user-attachments/assets/a1a27fd5-f91c-482e-a8e8-5f962006e38a" />


### 📈 Health Tracking
Track important health metrics:
- Blood Pressure
- Pulse Rate
- Body Temperature
- Oxygen Saturation (SpO₂)
- Weight Monitoring

<img width="1470" height="798" alt="image" src="https://github.com/user-attachments/assets/dd4cf813-82e7-4065-951f-9d79dcd90f00" />


### 📄 Medical Report Summary
- Upload and analyze medical reports automatically
- Extract key findings and important health indicators
- Generate concise and easy-to-understand summaries



### 🚨 Emergency Assistance
Provides emergency contact information and alerts for critical conditions.

---

# 📂 Project Structure

```text
HealthMate-AI/
│
├── assets/
│   ├── login_hero.png
│   └── mic_recorder.html
│
├── healthmate/
│   ├── __init__.py
│   ├── ai.py
│   ├── config.py
│   ├── data.py
│   ├── nlp.py
│   └── ui.py
│
├── model_artifacts/
│   ├── cols.pkl
│   ├── le.pkl
│   ├── model.pkl
│   ├── severity.pkl
│   └── symlist.pkl
│
├── .env
├── Chatbot.ipynb
├── healthmate_chatbot.py
├── requirements.txt
└── README.md
```

---

# 🛠️ Technologies Used

- Python
- Streamlit
- Machine Learning
- NLP (Natural Language Processing)
- Pandas
- NumPy
- Scikit-Learn
- Pickle
- HTML/CSS
- Generative AI APIs

---

# 📦 Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/HealthMate-AI.git
cd HealthMate-AI
```

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 📁 Dataset Setup

Place the required CSV datasets in the project root directory.

Required files:

```text
Final_Augmented_dataset_Diseases_and_Symptoms.csv
medical_dataset.csv
Symptom-severity.csv
Testing.csv
train_data_chatbot.csv
```

If your files are stored elsewhere, update the paths in the data loading functions.

---

# 🔐 Environment Variables

Create a `.env` file in the root directory.

Example:

```env
API_KEY=your_api_key_here
```

Replace the values with your actual credentials.

---

# ▶️ Running the Application

```bash
streamlit run healthmate_chatbot.py
```

Or

```bash
python -m streamlit run healthmate_chatbot.py
```

Open:

```text
http://localhost:8501
```

---

# 🤖 Machine Learning Components

The project uses pre-trained model artifacts:

| File | Purpose |
|--------|---------|
| model.pkl | Disease Prediction Model |
| le.pkl | Label Encoder |
| cols.pkl | Feature Columns |
| severity.pkl | Symptom Severity Mapping |
| symlist.pkl | Symptom List |

---

# 🎙️ Voice Interaction

### Mobile Devices
Use your keyboard microphone button to speak symptoms.

### Desktop
Use browser speech recognition support.

Examples:

- "I have fever and headache"
- "I am feeling chest pain"
- "Suggest a diet plan for diabetes"

---

# 🚨 Emergency Contacts (India)

| Service | Number |
|----------|---------|
| Ambulance | 108 |
| National Emergency | 112 |
| Health Helpline | 1800-180-1104 |
| Maternal & Child Ambulance | 102 |

---

# 🔮 Future Enhancements

- Doctor Appointment Booking
- Medicine Recommendation
- Medical Report Analysis
- Multi-Language Support
- AI Voice Assistant
- Health Risk Prediction
- Wearable Device Integration

---

# 👨‍💻 Author

**Ankit Chowdhary**

B.Tech CSE (Data Science & Machine Learning)

Healthcare AI | Machine Learning | NLP | Full-Stack Development

---

⭐ If you found this project useful, consider giving it a star on GitHub.
