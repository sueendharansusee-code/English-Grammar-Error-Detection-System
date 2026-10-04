# English Grammar Error Detection System

An educational NLP web application that analyzes English text to detect, explain, and correct grammar, spelling, punctuation, capitalization, and writing errors.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-black.svg)
![NLP](https://img.shields.io/badge/NLP-NLTK%20%7C%20LanguageTool-orange.svg)

---

## 🌟 Key Features

1. **Multi-Category Error Detection**:
   - **Subject-Verb Agreement**: Identifies mismatched subject/verb number and person (e.g., *"He go"* $\rightarrow$ *"He goes"*, *"They is"* $\rightarrow$ *"They are"*).
   - **Basic Spelling Mistakes**: Catches common typos (*"teh"*, *"definately"*, *"recieve"*, *"grammer"*).
   - **Missing Punctuation**: Flags missing end periods, missing question marks on interrogatives, and spacing after commas.
   - **Incorrect Capitalization**: Highlights uncapitalized pronoun *"I"*, sentence starters, days, months, and languages.
   - **Repeated Words**: Detects accidental duplicate words (*"the the"*, *"is is"*).
   - **Common Grammatical Patterns & Homophones**: Article usage (*"a apple"* $\rightarrow$ *"an apple"*), confused homophones (*"your/you're"*, *"their/there"*, *"its/it's"*, *"less/fewer"*).

2. **Interactive UI & Educational Dashboard**:
   - Live word and character counter.
   - Interactive highlighted text view displaying color-coded error markers.
   - Detailed issue breakdown cards showing original phrase, suggested fix, error badge, and detailed rule explanation.
   - Grammar Score dial (0 - 100%).
   - Metric cards counting Total Errors, Correct Sentences, and Suggestions.

3. **Hybrid NLP & Graceful Fallback**:
   - Uses **LanguageTool** (`language_tool_python`) if available on the system.
   - Automatic seamless fallback to **NLTK + Custom Pattern Engine** if Java/LanguageTool service is offline.

4. **SQLite History Persistence**:
   - Automatically records all analysis checks into an embedded SQLite database (`grammar_history.db`).
   - Modal drawer to review past reports, inspect scores, reload historical text, or clear log records.

5. **Usability Extras**:
   - One-click **Copy Corrected Text**.
   - One-click **Quick Samples** for testing preset error categories.
   - Clear input & notification toast alerts.

---

## 📁 Repository Structure

```
grammar_error_detector/
├── backend/
│   ├── __init__.py
│   ├── app.py              # Flask app factory, REST API routes
│   ├── database.py         # SQLite database management & queries
│   ├── grammar_engine.py   # Hybrid NLP engine & LanguageTool fallback wrapper
│   └── rules.py            # Offline rule-based NLP error detectors
├── frontend/
│   └── index.html          # Standalone client entry point
├── static/
│   ├── css/
│   │   └── style.css       # Responsive styling, score dial, badge colors & error markers
│   └── js/
│       └── main.js         # Frontend controller, API calls & DOM manipulation
├── templates/
│   └── index.html          # Main Flask educational dashboard view
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python package dependencies
└── README.md               # Documentation & guide
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- **Python 3.8+** installed on your system.
- Optional: Java 8+ (required only if using `language-tool-python` server locally; app runs automatically using offline NLTK engine if Java is absent).

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/english-grammar-error-detector.git
cd english-grammar-error-detector
```

### Step 2: Set Up Virtual Environment
On Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Flask Application
```bash
python backend/app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 📡 REST API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Renders the main educational dashboard |
| `/api/analyze` | `POST` | Accepts `{ "text": "..." }`, runs analysis, stores result in SQLite, returns full report JSON |
| `/api/history` | `GET` | Returns list of historical analysis entries |
| `/api/history/<id>` | `GET` | Returns full detail for a specific historical entry |
| `/api/history` | `DELETE` | Clears all stored analysis history |
| `/api/samples` | `GET` | Returns pre-loaded sample sentences across error categories |

---

## 🧪 Testing the Application

1. Click on any of the **Quick Samples** pills (e.g., *Subject-Verb Agreement* or *Mixed Essay Paragraph*).
2. Click **Check Grammar**.
3. View the computed **Grammar Score**, error highlights, and explanation cards.
4. Click **Copy Corrected Text** to verify text synthesis.
5. Click **History Log** in the top navigation to view the saved entry in SQLite.

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
