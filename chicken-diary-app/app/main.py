from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from app.models import db, Diary
from dotenv import load_dotenv
import os
from uuid import UUID
from werkzeug.utils import secure_filename

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tag = request.args.get('tag')
    if tag:
        tag = tag.strip()
        diaries = Diary.query.filter(
            db.or_(
                Diary.tags.ilike(f'{tag},%'),
                Diary.tags.ilike(f'%,{tag},%'),
                Diary.tags.ilike(f'%,{tag}'),
                Diary.tags == tag
            )
        ).order_by(Diary.created_at.desc()).all()
    else:
        diaries = Diary.query.order_by(Diary.created_at.desc()).all()
    return render_template('index.html', diaries=diaries)

@app.route('/create', methods=['GET'])
def show_create_diary():
    return render_template('create_diary.html')

@app.route('/create', methods=['POST'])
def create_diary():
    try:
        title = request.form['title']
        content = request.form['content']
        tags = request.form.get('tags', '')
        image_path = None

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_path = filename

        new_diary = Diary(
            title=title, 
            content=content, 
            tags=tags,
            image_path=image_path if image_path else None
        )
        db.session.add(new_diary)
        db.session.commit()
        
        flash('日記が正常に作成されました', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        flash('日記の保存中にエラーが発生しました', 'error')
        return redirect(url_for('show_create_diary'))

@app.route('/diary/<uuid:diary_id>')
def view_diary(diary_id):
    diary = Diary.query.get_or_404(str(diary_id))
    return render_template('view_diary.html', diary=diary)

@app.route('/diary/<uuid:diary_id>/delete', methods=['POST'])
def delete_diary(diary_id):
    try:
        diary = Diary.query.get_or_404(str(diary_id))
        if diary.image_path:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], diary.image_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(diary)
        db.session.commit()
        flash('日記が削除されました', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        flash('日記の削除に失敗しました', 'error')
        return str(e), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)