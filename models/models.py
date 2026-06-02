from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Association table for Note ↔ Tag many-to-many
note_tags = db.Table(
    'note_tags',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
    db.Column('tag_id',  db.Integer, db.ForeignKey('tags.id'),  primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes    = db.relationship('Note',    backref='author',  lazy='dynamic', cascade='all,delete-orphan')
    subjects = db.relationship('Subject', backref='owner',   lazy='dynamic', cascade='all,delete-orphan')
    tags     = db.relationship('Tag',     backref='creator', lazy='dynamic', cascade='all,delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Subject(db.Model):
    __tablename__ = 'subjects'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    color      = db.Column(db.String(20),  default='#6366f1')
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship('Note', backref='subject', lazy='dynamic')

    def __repr__(self):
        return f'<Subject {self.name}>'


class Tag(db.Model):
    __tablename__ = 'tags'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'user_id'),)

    def __repr__(self):
        return f'<Tag {self.name}>'


class Note(db.Model):
    __tablename__ = 'notes'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    content     = db.Column(db.Text, default='')
    subject_id  = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    file_path   = db.Column(db.String(300), nullable=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public   = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(36), unique=True, nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = db.relationship('Tag', secondary=note_tags, backref='notes', lazy='subquery')

    @property
    def file_ext(self):
        if self.file_path:
            return self.file_path.rsplit('.', 1)[-1].lower()
        return None

    @property
    def is_pdf(self):
        return self.file_ext == 'pdf'

    @property
    def is_image(self):
        return self.file_ext in ('png', 'jpg', 'jpeg', 'gif', 'webp')

    def __repr__(self):
        return f'<Note {self.title}>'
