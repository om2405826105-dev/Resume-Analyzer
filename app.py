# ============================================================
# AI Resume Analyzer - Flask Backend
# Author: College Project
# Description: Main Flask application handling routes,
#              resume parsing, NLP analysis, and recommendations
# ============================================================

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import os
import json
import re
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# --- PDF / DOCX parsing ---
import PyPDF2
import docx

# --- NLP ---
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data (runs once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.download('punkt_tab', quiet=True)
except:
    pass

# ── App Configuration ─────────────────────────────────────
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max upload
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'resume_analyzer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'resume_analyzer_secret_2024'

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ── Load Skills Dataset ───────────────────────────────────
with open('data/skills_dataset.json', 'r', encoding='utf-8') as f:
    SKILLS_DATA = json.load(f)

ALL_SKILLS = [s.lower() for s in SKILLS_DATA['all_skills']]
CAREER_PATHS = SKILLS_DATA['career_paths']
IMPROVEMENT_RULES = SKILLS_DATA['improvement_rules']

# ── Database Setup ────────────────────────────────────────
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Analysis(db.Model):
    __tablename__ = 'analyses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # allow old records to exist
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    filename = db.Column(db.String(255))
    skills = db.Column(db.Text)
    score = db.Column(db.Integer)
    top_career = db.Column(db.String(100))
    created_at = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    """Initialize SQLite database and create tables if not exist."""
    with app.app_context():
        db.create_all()
        try:
            conn = sqlite3.connect('resume_analyzer.db')
            cursor = conn.cursor()
            cursor.execute('ALTER TABLE analyses ADD COLUMN user_id INTEGER')
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            pass # Column already exists or table doesn't exist

init_db()

# ── Helper: Allowed File ──────────────────────────────────
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── Resume Text Extraction ────────────────────────────────
def extract_text_from_pdf(filepath):
    """Extract raw text from a PDF file using PyPDF2."""
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {e}")
    return text

def extract_text_from_docx(filepath):
    """Extract raw text from a DOCX file using python-docx."""
    text = ""
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"[ERROR] DOCX extraction failed: {e}")
    return text

def extract_text(filepath):
    """Dispatch to correct extractor based on file extension."""
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(filepath)
    elif ext == 'docx':
        return extract_text_from_docx(filepath)
    return ""

# ── Skill Extraction using NLP ────────────────────────────
def extract_skills(text):
    """
    Extract technical skills from resume text using NLTK tokenization
    and keyword matching against our skills dataset.
    """
    text_lower = text.lower()
    found_skills = []

    # Tokenize and remove stopwords
    try:
        tokens = word_tokenize(text_lower)
        stop_words = set(stopwords.words('english'))
        tokens = [t for t in tokens if t not in stop_words]
    except Exception:
        tokens = text_lower.split()

    # Match multi-word and single-word skills
    for skill in SKILLS_DATA['all_skills']:
        skill_lower = skill.lower()
        # Check for exact phrase match in full text
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            if skill not in found_skills:
                found_skills.append(skill)

    return found_skills

# ── Resume Scoring ────────────────────────────────────────
def calculate_score(text, skills):
    """
    Calculate a resume score out of 100 based on:
    - Number of skills found          (30 pts)
    - Presence of contact info        (20 pts)
    - Education section detected      (15 pts)
    - Projects section detected       (15 pts)
    - Experience / internship section (10 pts)
    - Certifications mentioned        (10 pts)
    """
    score = 0
    text_lower = text.lower()

    # Skills score (up to 30)
    skill_score = min(len(skills) * 2, 30)
    score += skill_score

    # Contact info (up to 20)
    if re.search(r'[\w.-]+@[\w.-]+\.\w+', text):       # Email
        score += 8
    if re.search(r'\+?\d[\d\s\-]{8,}', text):           # Phone
        score += 7
    if re.search(r'linkedin\.com', text_lower):          # LinkedIn
        score += 5

    # Education (15)
    if any(kw in text_lower for kw in ['education', 'university', 'college', 'b.tech', 'bachelor', 'b.e.', 'degree']):
        score += 15

    # Projects (15)
    if any(kw in text_lower for kw in ['project', 'developed', 'built', 'implemented', 'designed']):
        score += 15

    # Experience (10)
    if any(kw in text_lower for kw in ['experience', 'internship', 'intern', 'worked', 'employment']):
        score += 10

    # Certifications (10)
    if any(kw in text_lower for kw in ['certification', 'certified', 'certificate', 'course', 'udemy', 'coursera']):
        score += 10

    return min(score, 100)

# ── Career Recommendation ─────────────────────────────────
def recommend_careers(skills):
    """
    Match extracted skills against each career path.
    Returns a sorted list of (career, match_percentage, missing_skills).
    """
    skills_lower = [s.lower() for s in skills]
    recommendations = []

    for career, data in CAREER_PATHS.items():
        required = data['required_skills']
        required_lower = [s.lower() for s in required]

        matched = [s for s in required_lower if s in skills_lower]
        missing = [s for s in required if s.lower() not in skills_lower]
        match_pct = round((len(matched) / len(required)) * 100)

        recommendations.append({
            'career': career,
            'match_percentage': match_pct,
            'matched_skills': [s for s in required if s.lower() in skills_lower],
            'missing_skills': missing,
            'roadmap': data['roadmap'],
            'description': data['description'],
            'avg_salary': data['avg_salary'],
            'icon': data['icon']
        })

    # Sort by match percentage descending
    recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
    return recommendations

# ── Improvement Suggestions ───────────────────────────────
def get_improvement_suggestions(text, skills):
    """
    Analyze the resume text and return a list of actionable improvement tips.
    """
    suggestions = []
    text_lower = text.lower()

    if 'github' not in text_lower:
        suggestions.append(IMPROVEMENT_RULES['no_github'])
    if 'linkedin' not in text_lower:
        suggestions.append(IMPROVEMENT_RULES['no_linkedin'])
    if not re.search(r'[\w.-]+@[\w.-]+\.\w+', text):
        suggestions.append(IMPROVEMENT_RULES['no_email'])
    if not re.search(r'\+?\d[\d\s\-]{8,}', text):
        suggestions.append(IMPROVEMENT_RULES['no_phone'])
    if len(text.split()) < 200:
        suggestions.append(IMPROVEMENT_RULES['short_resume'])
    if 'project' not in text_lower:
        suggestions.append(IMPROVEMENT_RULES['no_projects'])
    if not any(kw in text_lower for kw in ['%', 'improved', 'increased', 'reduced', 'achieved']):
        suggestions.append(IMPROVEMENT_RULES['no_achievements'])
    if not any(verb in text_lower for verb in ['developed', 'implemented', 'designed', 'optimized', 'built']):
        suggestions.append(IMPROVEMENT_RULES['weak_verbs'])
    if not any(kw in text_lower for kw in ['education', 'b.tech', 'degree', 'university']):
        suggestions.append(IMPROVEMENT_RULES['no_education'])
    if not any(kw in text_lower 
                for kw in ['certification', 'certified', 'certificate']):
        suggestions.append(IMPROVEMENT_RULES['no_certifications'])

    return suggestions

# ── Save to Database ──────────────────────────────────────
def save_to_db(name, email, filename, skills, score, top_career):
    """Persist analysis results to SQLite database."""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        analysis = Analysis(
            user_id=user_id,
            name=name,
            email=email,
            filename=filename,
            skills=','.join(skills),
            score=score,
            top_career=top_career,
            created_at=datetime.now().isoformat()
        )
        db.session.add(analysis)
        db.session.commit()
    except Exception as e:
        print(f"[ERROR] DB save failed: {e}")

# ── Routes ─────────────────────────────────────────────────

@app.route('/')
def home():
    """Render the landing / home page."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
            
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login an existing user."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('upload_page'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout the user."""
    logout_user()
    return redirect(url_for('home'))

@app.route('/upload')
@login_required
def upload_page():
    """Render the resume upload page."""
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """
    Main analysis endpoint.
    - Accepts multipart form with resume file
    - Extracts text, skills, calculates score
    - Returns JSON with full analysis result
    """
    # Validate file
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400

    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)

    # Get form fields
    name  = request.form.get('name', 'Anonymous')
    email = request.form.get('email', '')

    # --- Core Analysis Pipeline ---
    text         = extract_text(filepath)
    if not text.strip():
        return jsonify({'error': 'Could not extract text from the resume. Please check the file.'}), 400

    skills       = extract_skills(text)
    score        = calculate_score(text, skills)
    careers      = recommend_careers(skills)
    suggestions  = get_improvement_suggestions(text, skills)
    top_career   = careers[0]['career'] if careers else 'General'

    # Save to DB
    save_to_db(name, email, filename, skills, score, top_career)

    # Build skill distribution for chart
    skill_categories = {
        'Programming': ['Python', 'Java', 'C++', 'C', 'JavaScript', 'TypeScript', 'R', 'Go'],
        'Web': ['HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Bootstrap'],
        'Data/ML': ['Machine Learning', 'Deep Learning', 'Pandas', 'NumPy', 'TensorFlow', 'Scikit-learn'],
        'Database': ['SQL', 'MySQL', 'MongoDB', 'PostgreSQL', 'SQLite', 'Redis'],
        'DevOps/Tools': ['Git', 'Docker', 'Kubernetes', 'Linux', 'CI/CD', 'Jenkins'],
        'Other': []
    }

    skill_dist = {cat: 0 for cat in skill_categories}
    for skill in skills:
        placed = False
        for cat, cat_skills in skill_categories.items():
            if skill in cat_skills:
                skill_dist[cat] += 1
                placed = True
                break
        if not placed:
            skill_dist['Other'] += 1

    # Remove zero-count categories
    skill_dist = {k: v for k, v in skill_dist.items() if v > 0}

    return jsonify({
        'success': True,
        'name': name,
        'email': email,
        'filename': filename,
        'skills': skills,
        'skill_count': len(skills),
        'score': score,
        'careers': careers,
        'top_career': top_career,
        'suggestions': suggestions,
        'skill_distribution': skill_dist,
        'word_count': len(text.split())
    })

@app.route('/results')
def results_page():
    """Render the results display page."""
    return render_template('results.html')

@app.route('/history')
@login_required
def history():
    """Show past analysis history from DB."""
    analyses_query = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).limit(20).all()
    analyses = []
    for row in analyses_query:
        analyses.append({
            'id': row.id, 'name': row.name, 'email': row.email,
            'filename': row.filename, 'skills': row.skills, 'score': row.score,
            'top_career': row.top_career, 'created_at': row.created_at
        })
    return render_template('history.html', analyses=analyses)

# ── Run ───────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)
