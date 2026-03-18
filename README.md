
# Firebase Policy Chatbot

AI-powered government policy analysis platform that helps citizens understand, compare, and access information about government policies and schemes.

## Features

* Firebase Authentication – Secure user registration and login
* Policy Comparison – AI-powered side-by-side policy analysis
* Sentiment Analysis – Multi-stakeholder perspective analysis
* Eligibility Checker – Personalized government scheme recommendations
* Regional Policies – State-specific policy information
* General Query – Natural language Q\&A about policies
* Multi-language Support – English, Hindi, Punjabi, Tamil, Bengali

## Technology Stack

* **Frontend:** Streamlit, Plotly, Pyrebase4
* **Backend:** Flask, Firebase Admin SDK, Google Gemini AI
* **Database:** Firebase Firestore
* **Authentication:** Firebase Auth
* **AI:** Google Gemini 1.5 Flash

## Quick Start

### Prerequisites

* Python 3.8+
* Firebase project with Firestore enabled
* Google Gemini API key

### Installation

#### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/firebase-policy-chatbot.git
cd firebase-policy-chatbot
```

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup

```bash
cd ../frontend
pip install -r requirements.txt
```

#### Environment Configuration

```bash
# Create .env files in both backend and frontend directories
# Add your Firebase configuration and Gemini API key
```

### Firebase Setup

* Download `serviceAccountKey.json` from Firebase Console
* Place it in the `firebase/` directory
* Enable Authentication and Firestore in Firebase Console

### Run the Application

#### Terminal 1 – Backend

```bash
cd backend
python app.py
```

#### Terminal 2 – Frontend

```bash
cd frontend
streamlit run streamlit_app.py
```

### Access the Application

* Frontend: [http://localhost:8501](http://localhost:8501)
* Backend API: [http://localhost:5000](http://localhost:5000)

---

## Project Structure

```
firebase-policy-chatbot/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── firebase_config.py        # Firebase configuration
│   └── requirements.txt          # Backend dependencies
├── frontend/
│   ├── streamlit_app.py         # Main Streamlit application
│   ├── firebase_config.py       # Firebase client config
│   └── requirements.txt         # Frontend dependencies
├── firebase/
│   ├── firebase-config.js       # Firebase web config reference
│   └── serviceAccountKey.json   # Firebase admin key (not in git)
└── README.md
```

---

## Features Overview

### Policy Comparison

Compare two government policies with comprehensive AI analysis including:

* Implementation differences and similarities
* Target beneficiaries and eligibility criteria
* Budget allocation and funding sources
* Success metrics and performance indicators
* Interactive charts and visualizations

### Sentiment Analysis

Analyze public sentiment and stakeholder perspectives with:

* Multi-stakeholder sentiment breakdown
* Visual sentiment dashboards with charts
* Regional variation insights
* Historical sentiment trends

### Eligibility Checker

Get personalized government scheme recommendations based on:

* Personal information (age, income, occupation)
* Location and demographic details
* Family composition and background
* Detailed eligibility analysis with application guidance

### Regional Policies

Access comprehensive state-specific information including:

* State government schemes and initiatives
* Budget allocation by department
* Local implementation details
* Comparison with national policies

---

## Configuration

### Firebase Setup

* Create a Firebase project at [https://console.firebase.google.com/](https://console.firebase.google.com/)
* Enable Authentication with Email/Password provider
* Enable Firestore Database
* Download service account key and place in `firebase/` directory
* Get web app configuration for client-side authentication

### Gemini AI Setup

* Get API key from Google AI Studio ([https://makersuite.google.com/](https://makersuite.google.com/))
* Add the API key to your environment variables
* Configure rate limiting and error handling

---

## Security Features

* Environment variables for all sensitive data
* Firebase Authentication with secure token validation
* Firestore security rules for data protection
* CORS configuration for secure API access
* Input validation and sanitization


---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---


