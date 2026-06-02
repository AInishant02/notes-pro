import os
import json
from dotenv import load_dotenv
load_dotenv()
import uuid
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, jsonify, send_from_directory, abort)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ── App Config ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}

from models.models import db, User, Note, Subject, Tag

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── Auth ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        else:
            user = User(username=username, email=email,
                        password=generate_password_hash(password))
            db.session.add(user)
            db.session.flush()
            for name, color in [('English', '#f59e0b'), ('Math', '#6366f1'), ('Science', '#10b981')]:
                db.session.add(Subject(name=name, color=color, user_id=user.id))
            db.session.commit()
            login_user(user)
            flash('Account created! Welcome to Notes Pro.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=request.form.get('remember'))
            flash('Welcome back!', 'success')
            next_url = request.args.get('next')
            if next_url and not next_url.startswith('/'):
                next_url = None
            return redirect(next_url or url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ── Dashboard ──────────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated_at.desc()).all()
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', notes=notes, subjects=subjects,
                           recent=notes[:6], total=len(notes), sub_count=len(subjects))

# ── Notes CRUD ─────────────────────────────────────────────────────────────
@app.route('/notes/create', methods=['GET', 'POST'])
@login_required
def create_note():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        subject_id = request.form.get('subject_id') or None
        tags_raw = request.form.get('tags', '')
        is_public = bool(request.form.get('is_public'))
        if not title:
            flash('Title is required.', 'danger')
            return render_template('create_note.html', subjects=subjects)
        file_path = None
        file = request.files.get('file')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = filename
        note = Note(title=title, content=content,
                    subject_id=int(subject_id) if subject_id else None,
                    file_path=file_path, user_id=current_user.id,
                    is_public=is_public,
                    share_token=str(uuid.uuid4()) if is_public else None)
        db.session.add(note)
        db.session.flush()
        for tag_name in [t.strip() for t in tags_raw.split(',') if t.strip()]:
            tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
            if not tag:
                tag = Tag(name=tag_name, user_id=current_user.id)
                db.session.add(tag)
                db.session.flush()
            note.tags.append(tag)
        db.session.commit()
        flash('Note created!', 'success')
        return redirect(url_for('view_note', note_id=note.id))
    return render_template('create_note.html', subjects=subjects)

@app.route('/notes/<int:note_id>')
@login_required
def view_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id and not note.is_public:
        abort(403)
    return render_template('view_note.html', note=note)

@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        note.title = request.form.get('title', '').strip()
        note.content = request.form.get('content', '')
        subject_id = request.form.get('subject_id')
        note.subject_id = int(subject_id) if subject_id else None
        note.is_public = bool(request.form.get('is_public'))
        if note.is_public and not note.share_token:
            note.share_token = str(uuid.uuid4())
        note.updated_at = datetime.utcnow()
        note.tags = []
        tags_raw = request.form.get('tags', '')
        for tag_name in [t.strip() for t in tags_raw.split(',') if t.strip()]:
            tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
            if not tag:
                tag = Tag(name=tag_name, user_id=current_user.id)
                db.session.add(tag)
                db.session.flush()
            note.tags.append(tag)
        file = request.files.get('file')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            note.file_path = filename
        db.session.commit()
        flash('Note updated!', 'success')
        return redirect(url_for('view_note', note_id=note.id))
    return render_template('edit_note.html', note=note, subjects=subjects)

@app.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted.', 'info')
    return redirect(url_for('dashboard'))

# ── Public Share ───────────────────────────────────────────────────────────
@app.route('/share/<token>')
def shared_note(token):
    note = Note.query.filter_by(share_token=token, is_public=True).first_or_404()
    return render_template('view_note.html', note=note, shared=True)

# ── Subjects ───────────────────────────────────────────────────────────────
@app.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        color = request.form.get('color', '#6366f1')
        if name:
            sub = Subject(name=name, color=color, user_id=current_user.id)
            db.session.add(sub)
            db.session.commit()
            flash('Subject added!', 'success')
    subs = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('subjects.html', subjects=subs)

@app.route('/subjects/<int:sub_id>/delete', methods=['POST'])
@login_required
def delete_subject(sub_id):
    sub = Subject.query.get_or_404(sub_id)
    if sub.user_id != current_user.id:
        abort(403)
    db.session.delete(sub)
    db.session.commit()
    flash('Subject deleted.', 'info')
    return redirect(url_for('subjects'))

# ── Search ─────────────────────────────────────────────────────────────────
@app.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    subject_id = request.args.get('subject', '')
    results = []
    if q or subject_id:
        query = Note.query.filter_by(user_id=current_user.id)
        if q:
            like = f'%{q}%'
            query = query.filter((Note.title.ilike(like)) | (Note.content.ilike(like)))
        if subject_id:
            query = query.filter_by(subject_id=int(subject_id))
        results = query.order_by(Note.updated_at.desc()).all()
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('search.html', results=results, q=q,
                           subjects=subjects, subject_id=subject_id)

# ── File Serve ─────────────────────────────────────────────────────────────
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ── AI Assistant Page ────────────────────────────────────────────────────
@app.route('/notes/<int:note_id>/ai')
@login_required
def ai_assistant(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    return render_template('ai_assistant.html', note=note)

# ── API: AI Summarizer ─────────────────────────────────────────────────────
@app.route('/api/ai/summarize', methods=['POST'])
@login_required
def ai_summarize():
    data = request.get_json()
    content = data.get('content', '')
    action = data.get('action', 'summarize')
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        return jsonify({'error': 'AI API key not configured. Set GROQ_API_KEY env var.'}), 503
    import requests as req_lib
    prompts = {
        'summarize': f"Summarize the following study notes concisely in bullet points:\n\n{content}",
        'quiz': """Generate exactly 5 multiple-choice questions from the notes below.
For each question use this exact format:
1. Question text
A. Option
B. Option
C. Option
D. Option
Answer: A
Explanation: Brief explanation

Notes:\n""" + content,
        'flashcards': """Create exactly 8 flashcard pairs from the notes below.
Use this exact format for each card:
Q: Question
A: Answer

Notes:\n""" + content,
    }
    prompt = prompts.get(action, prompts['summarize'])
    try:
        resp = req_lib.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={'model': 'llama-3.3-70b-versatile', 'messages': [{'role': 'user', 'content': prompt}]},
            timeout=30
        )
        if not resp.ok:
            return jsonify({'error': f'API error {resp.status_code}: {resp.text}'}), 500
        text = resp.json()['choices'][0]['message']['content']
        return jsonify({'result': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
