import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Diary(db.Model):
    __tablename__ = 'diaries'
    
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    title = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )
    
    content = db.Column(
        db.Text,
        nullable=False
    )
    
    image_path = db.Column(
        db.String(255),
        nullable=True
    )

    tags = db.Column(
        db.String(255),
        nullable=True
    )
    
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    @validates('title')
    def validate_title(self, key, title):
        if not title or not title.strip():
            raise ValueError('タイトルは必須です')
        if len(title) > 100:
            raise ValueError('タイトルは100文字以内である必要があります')
        return title.strip()

    @validates('image_path')
    def validate_image_path(self, key, path):
        if path is not None:
            if not path.strip():
                return None
            if len(path) > 255:
                raise ValueError('画像パスが長すぎます')
            return path.strip()
        return None

    def __repr__(self):
        return f'<Diary {self.id}: {self.title}>'
