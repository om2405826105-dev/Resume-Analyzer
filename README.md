# ⚡ AI Resume Analyzer & Career Path Recommendation System
### College Project | Python Flask + NLP + Chart.js

---

## 📁 Project Folder Structure

```
resume_analyzer/
│
├── app.py                        ← Flask backend (main server)
├── requirements.txt              ← Python dependencies
├── resume_analyzer.db            ← SQLite database (auto-created on first run)
│
├── data/
│   └── skills_dataset.json       ← Skills data + career paths dataset
│
├── static/
│   ├── css/
│   │   └── style.css             ← All styling (dark theme + responsive)
│   ├── js/
│   │   ├── upload.js             ← Upload form logic + loading animation
│   │   └── results.js            ← Results rendering + Chart.js charts
│   └── uploads/                  ← Uploaded resumes stored here
│
└── templates/
    ├── index.html                ← Home / landing page
    ├── upload.html               ← Resume upload page
    ├── results.html              ← Analysis results page
    └── history.html              ← Past analyses history page
```

---

## 🛠️ Technology Stack

| Layer      | Technology                         |
|------------|-------------------------------------|
| Frontend   | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend    | Python 3.10+, Flask                 |
| NLP        | NLTK (tokenization + stopwords)     |
| Parsing    | PyPDF2 (PDF), python-docx (DOCX)    |
| Database   | SQLite (via Python sqlite3 module)  |
| Charts     | Chart.js 4.4                        |
| Icons      | Font Awesome 6                      |
| Fonts      | Google Fonts (Syne + DM Sans)       |

---

## ⚙️ Step-by-Step Setup Instructions

### Step 1 — Prerequisites
Make sure you have installed:
- Python 3.10 or higher → https://python.org
- pip (comes with Python)

Verify:
```bash
python --version
pip --version
```

---

### Step 2 — Navigate to Project Folder
```bash
cd resume_analyzer
```

---

### Step 3 — Create a Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

---

### Step 4 — Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- PyPDF2 (PDF text extraction)
- python-docx (DOCX text extraction)
- NLTK (Natural Language Processing)
- Werkzeug (file utilities)

---

### Step 5 — Download NLTK Data
The app downloads required NLTK data automatically on first run.
If it fails, run this manually:
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

---

### Step 6 — Run the Application
```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

---

### Step 7 — Open in Browser
Open your browser and go to:
```
http://localhost:5000
```

---

## 🚀 How to Use

1. Go to `http://localhost:5000`
2. Click **"Analyze My Resume"**
3. Enter your name and email (optional)
4. Upload your PDF or DOCX resume
5. Click **"Analyze My Resume"** button
6. View your results:
   - Resume Score (out of 100)
   - Detected Skills
   - Career Recommendations with match %
   - Skill Gap Analysis
   - Career Roadmap
   - Improvement Suggestions

---

## 📊 Features Explained

### Resume Scoring (out of 100)
| Component          | Points |
|--------------------|--------|
| Skills found       | Up to 30 |
| Email present      | 8      |
| Phone present      | 7      |
| LinkedIn link      | 5      |
| Education section  | 15     |
| Projects section   | 15     |
| Experience section | 10     |
| Certifications     | 10     |

### Career Paths Analyzed
- 💻 Software Developer
- 📊 Data Scientist
- 🌐 Web Developer
- 📈 Data Analyst
- 🔐 Cyber Security Engineer

### Charts Generated
1. **Resume Score** — Doughnut gauge chart
2. **Skill Distribution** — Pie chart by category
3. **Career Match** — Horizontal bar chart

---

## 🗄️ Database
The app uses SQLite. The database file `resume_analyzer.db` is auto-created in the project root on first run. View history at `http://localhost:5000/history`.

---

## ❗ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `NLTK data not found` | Run the manual download command in Step 5 |
| Can't extract text from PDF | Ensure the PDF is not scanned/image-only |
| Port already in use | Change port in `app.py`: `app.run(port=5001)` |
| File upload fails | Check `static/uploads/` folder exists (auto-created) |

---

## 📝 Project Details
- **Project Title:** AI Resume Analyzer and Career Path Recommendation System
- **Technology:** Python Flask + NLTK + PyPDF2 + Chart.js
- **Database:** SQLite
- **Purpose:** College project demonstrating NLP, web development, and data visualization

---
*Built with ❤️ as a Computer Engineering College Project*
