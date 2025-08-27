
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from forms import ProjectForm, ProgressEntryForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
db_url = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELS
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    # 'progress' attribute between start_date and end_date
    progress = db.Column(db.Text, nullable=True)  # summary of progress
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=True, default='Planned')

    entries = db.relationship('ProgressEntry', backref='project', lazy=True, cascade='all, delete-orphan')

class ProgressEntry(db.Model):
    __tablename__ = 'progress_entries'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# CLI to init db
@app.cli.command('init-db')
def init_db_cmd():
    db.create_all()
    print('Initialized the database.')

@app.before_first_request
def init_db_once():
    # Ensure tables exist in both local and hosted environments
    db.create_all()

# ROUTES
@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    projects = Project.query.order_by(Project.id.desc())
    if q:
        like = f"%{q}%"
        projects = projects.filter(
            db.or_(
                Project.name.ilike(like),
                Project.description.ilike(like),
                Project.progress.ilike(like),
                Project.status.ilike(like)
            )
        )
    return render_template('index.html', projects=projects.all(), q=q)

@app.route('/project/new', methods=['GET', 'POST'])
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            progress=form.progress.data,   # positioned between start and end date in the form
            end_date=form.end_date.data,
            status=form.status.data or 'Planned'
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created', 'success')
        return redirect(url_for('index'))
    return render_template('form.html', form=form, title='New Project')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    entry_form = ProgressEntryForm()
    entries = ProgressEntry.query.filter_by(project_id=project.id).order_by(ProgressEntry.created_at.desc()).all()
    return render_template('detail.html', project=project, entry_form=entry_form, entries=entries)

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        db.session.commit()
        flash('Project updated', 'success')
        return redirect(url_for('project_detail', project_id=project.id))
    return render_template('form.html', form=form, title='Edit Project')

@app.route('/project/<int:project_id>/delete', methods=['POST', 'GET'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted', 'info')
        return redirect(url_for('index'))
    return render_template('confirm_delete.html', project=project)

@app.route('/project/<int:project_id>/entries', methods=['POST'])
def add_entry(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProgressEntryForm()
    if form.validate_on_submit():
        entry = ProgressEntry(project_id=project.id, content=form.content.data)
        db.session.add(entry)
        db.session.commit()
        flash('Progress entry added', 'success')
    else:
        flash('Could not add entry. Make sure content is not empty.', 'danger')
    return redirect(url_for('project_detail', project_id=project.id))

@app.route('/entry/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    entry = ProgressEntry.query.get_or_404(entry_id)
    project_id = entry.project_id
    db.session.delete(entry)
    db.session.commit()
    flash('Progress entry deleted', 'info')
    return redirect(url_for('project_detail', project_id=project_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
