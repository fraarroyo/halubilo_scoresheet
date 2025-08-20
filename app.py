from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scoresheet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/teams'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=True)  # Assign to specific activity
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to activity
    activity = db.relationship('Activity', backref='assigned_users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='team', lazy=True)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    max_score = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='activity', lazy=True)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class TeamForm(FlaskForm):
    name = StringField('Team Name')
    image = FileField('Team Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed!')
    ])
    csv_file = FileField('Bulk Upload CSV', validators=[
        FileAllowed(['csv'], 'Only CSV files are allowed!')
    ])
    submit = SubmitField('Add Individual Team')
    bulk_submit = SubmitField('Upload CSV')

class ActivityForm(FlaskForm):
    name = StringField('Activity Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    max_score = IntegerField('Maximum Score', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    submit = SubmitField('Add Activity')

class QuickUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired(), Length(min=6)])
    activity_id = SelectField('Assign to Activity', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create User for Activity')

class ScoreForm(FlaskForm):
    team_id = SelectField('Team', coerce=int, validators=[DataRequired()])
    activity_id = SelectField('Activity', coerce=int, validators=[DataRequired()])
    score = IntegerField('Score', validators=[DataRequired(), NumberRange(min=0)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit Score')

# Decorator for admin-only routes
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    teams = Team.query.all()
    activities = Activity.query.all()
    scores = Score.query.all()
    
    # Calculate total scores for each team
    team_scores = {}
    for team in teams:
        team_scores[team.id] = sum(score.score for score in team.scores)
    
    # Sort teams by total score (descending)
    sorted_teams = sorted(teams, key=lambda x: team_scores.get(x.id, 0), reverse=True)
    
    return render_template('index.html', 
                         teams=sorted_teams, 
                         activities=activities, 
                         scores=scores,
                         team_scores=team_scores)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match', 'error')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('register.html', form=form)
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    teams = Team.query.all()
    activities = Activity.query.all()
    users = User.query.all()
    
    # Calculate statistics
    team_stats = {}
    for team in teams:
        team_scores = [score.score for score in team.scores]
        team_stats[team.id] = {
            'name': team.name,
            'image_filename': team.image_filename,
            'total_score': sum(team_scores),
            'average_score': sum(team_scores) / len(team_scores) if team_scores else 0,
            'activities_completed': len(team_scores),
            'highest_score': max(team_scores) if team_scores else 0
        }
    
    # Sort teams by total score
    sorted_teams = sorted(team_stats.values(), key=lambda x: x['total_score'], reverse=True)
    
    return render_template('admin_dashboard.html', 
                         team_stats=sorted_teams,
                         activities=activities,
                         users=users,
                         teams=teams)

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    teams = Team.query.all()
    activities = Activity.query.all()
    user_scores = Score.query.filter_by(created_by=current_user.id).order_by(Score.created_at.desc()).all()
    
    # Calculate total scores for each team
    team_scores = {}
    for team in teams:
        team_scores[team.id] = sum(score.score for score in team.scores)
    
    # Sort teams by total score (descending)
    sorted_teams = sorted(teams, key=lambda x: team_scores.get(x.id, 0), reverse=True)
    
    return render_template('user_dashboard.html', 
                         teams=sorted_teams,
                         activities=activities,
                         user_scores=user_scores,
                         team_scores=team_scores)

@app.route('/teams', methods=['GET', 'POST'])
@login_required
@admin_required
def teams():
    form = TeamForm()
    if form.validate_on_submit():
        # Check if any input method is provided
        has_csv = form.csv_file.data and form.csv_file.data.filename
        has_individual = form.name.data and form.name.data.strip()
        
        if not has_csv and not has_individual:
            flash('Please provide a team name for individual creation or upload a CSV file.', 'warning')
            return redirect(url_for('teams'))
        
        if form.csv_file.data:
            # Handle CSV upload
            csv_file = form.csv_file.data
            if csv_file.filename.endswith('.csv'):
                try:
                    # Read the uploaded CSV file
                    file_content = csv_file.read()
                    # Use io.StringIO to read the file content as a string
                    file_stream = io.StringIO(file_content.decode('utf-8'))
                    csv_reader = csv.DictReader(file_stream)

                    teams_created = 0
                    teams_skipped = 0

                    # Process each row in the CSV
                    for row in csv_reader:
                        team_name = row.get('Team Name', '').strip()
                        if not team_name:
                            continue  # Skip empty rows
                        
                        # Check if team already exists
                        existing_team = Team.query.filter_by(name=team_name).first()
                        if existing_team:
                            teams_skipped += 1
                            continue

                        team = Team(name=team_name)
                        db.session.add(team)
                        teams_created += 1
                    
                    db.session.commit()
                    
                    if teams_created > 0:
                        flash(f'Successfully created {teams_created} teams from CSV!', 'success')
                    if teams_skipped > 0:
                        flash(f'Skipped {teams_skipped} existing teams.', 'warning')
                    if teams_created == 0 and teams_skipped == 0:
                        flash('No valid teams found in CSV file.', 'warning')
                        
                except csv.Error as e:
                    flash(f'Error reading CSV file: {e}', 'error')
                except Exception as e:
                    flash(f'An unexpected error occurred: {e}', 'error')
                    db.session.rollback()
            else:
                flash('Please select a valid CSV file.', 'error')
        elif form.name.data and form.name.data.strip():  # Only create individual team if name is provided
            # Handle individual team creation
            if form.image.data:
                # Handle individual team creation with image
                filename = secure_filename(form.image.data.filename)
                # Add timestamp to prevent filename conflicts
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.image.data.save(filepath)
                team = Team(name=form.name.data.strip(), image_filename=filename)
                db.session.add(team)
                db.session.commit()
                flash('Team added successfully!', 'success')
            else:
                # Handle individual team creation without image
                team = Team(name=form.name.data.strip())
                db.session.add(team)
                db.session.commit()
                flash('Team added successfully!', 'success')
        
        return redirect(url_for('teams'))
    
    teams = Team.query.all()
    return render_template('teams.html', form=form, teams=teams)

@app.route('/teams/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamForm(obj=team)
    
    if form.validate_on_submit():
        # Handle file upload
        if form.image.data:
            # Delete old image if it exists
            if team.image_filename:
                try:
                    old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], team.image_filename)
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                except OSError:
                    pass  # Ignore if file not found
            
            # Save new image
            filename = secure_filename(form.image.data.filename)
            # Add timestamp to prevent filename conflicts
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(filepath)
            team.image_filename = filename
        
        team.name = form.name.data
        db.session.commit()
        flash('Team updated successfully!', 'success')
        return redirect(url_for('teams'))
    
    return render_template('edit_team.html', form=form, team=team)

@app.route('/teams/<int:team_id>/delete')
@login_required
@admin_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    # Delete the image file if it exists
    if team.image_filename:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], team.image_filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except OSError:
            pass  # Ignore if file not found
    
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', 'success')
    return redirect(url_for('teams'))

@app.route('/activities', methods=['GET', 'POST'])
@login_required
@admin_required
def activities():
    form = ActivityForm()
    user_form = QuickUserForm()
    
    # Populate activity choices for user form
    user_form.activity_id.choices = [(activity.id, activity.name) for activity in Activity.query.all()]
    
    if form.validate_on_submit():
        activity = Activity(
            name=form.name.data,
            description=form.description.data,
            max_score=form.max_score.data
        )
        db.session.add(activity)
        db.session.commit()
        flash('Activity added successfully!', 'success')
        return redirect(url_for('activities'))
    
    if user_form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=user_form.username.data).first():
            flash('Username already exists', 'error')
        elif User.query.filter_by(email=user_form.email.data).first():
            flash('Email already registered', 'error')
        else:
            # Create new user assigned to specific activity
            user = User(
                username=user_form.username.data,
                email=user_form.email.data,
                role='user',  # Default role for quick-created users
                activity_id=user_form.activity_id.data  # Assign to selected activity
            )
            user.set_password(user_form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash(f'User {user.username} created successfully for activity!', 'success')
            return redirect(url_for('activities'))
    
    activities = Activity.query.all()
    return render_template('activities.html', form=form, user_form=user_form, activities=activities)

@app.route('/activities/<int:activity_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    form = ActivityForm(obj=activity)
    
    if form.validate_on_submit():
        activity.name = form.name.data
        activity.description = form.description.data
        activity.max_score = form.max_score.data
        db.session.commit()
        flash('Activity updated successfully!', 'success')
        return redirect(url_for('activities'))
    
    return render_template('edit_activity.html', form=form, activity=activity)

@app.route('/activities/<int:activity_id>/delete')
@login_required
@admin_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()
    flash('Activity deleted successfully!', 'success')
    return redirect(url_for('activities'))

@app.route('/scores', methods=['GET', 'POST'])
@login_required
def scores():
    form = ScoreForm()
    form.team_id.choices = [(team.id, team.name) for team in Team.query.all()]
    # Lock activity to assigned activity for non-admin users
    if current_user.role != 'admin' and getattr(current_user, 'activity_id', None):
        assigned_activity = Activity.query.get(current_user.activity_id)
        form.activity_id.choices = [(assigned_activity.id, assigned_activity.name)]
        # Ensure the correct value is set on both GET and POST
        form.activity_id.data = assigned_activity.id
    else:
        form.activity_id.choices = [(activity.id, activity.name) for activity in Activity.query.all()]
    
    if form.validate_on_submit():
        # Enforce activity lock serverside as well
        activity_id = form.activity_id.data
        if current_user.role != 'admin' and getattr(current_user, 'activity_id', None):
            activity_id = current_user.activity_id
        score = Score(
            team_id=form.team_id.data,
            activity_id=activity_id,
            score=form.score.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(score)
        db.session.commit()
        flash('Score submitted successfully!', 'success')
        return redirect(url_for('scores'))
    
    scores = Score.query.order_by(Score.created_at.desc()).all()

    # Build current standings: total score per team, sorted desc
    teams = Team.query.all()
    team_scores = {team.id: sum(s.score for s in team.scores) for team in teams}
    sorted_teams = sorted(teams, key=lambda t: team_scores.get(t.id, 0), reverse=True)

    return render_template('scores.html', form=form, scores=scores, teams=sorted_teams, team_scores=team_scores)

@app.route('/scores/<int:score_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_score(score_id):
    score = Score.query.get_or_404(score_id)
    
    # Users can only edit their own scores, admins can edit any
    if current_user.role != 'admin' and score.created_by != current_user.id:
        abort(403)
    
    form = ScoreForm(obj=score)
    form.team_id.choices = [(team.id, team.name) for team in Team.query.all()]
    if current_user.role != 'admin' and getattr(current_user, 'activity_id', None):
        assigned_activity = Activity.query.get(current_user.activity_id)
        form.activity_id.choices = [(assigned_activity.id, assigned_activity.name)]
        form.activity_id.data = assigned_activity.id
    else:
        form.activity_id.choices = [(activity.id, activity.name) for activity in Activity.query.all()]
    
    if form.validate_on_submit():
        score.team_id = form.team_id.data
        # Enforce activity lock when editing
        score.activity_id = (current_user.activity_id if current_user.role != 'admin' and getattr(current_user, 'activity_id', None)
                             else form.activity_id.data)
        score.score = form.score.data
        score.notes = form.notes.data
        db.session.commit()
        flash('Score updated successfully!', 'success')
        return redirect(url_for('scores'))
    
    return render_template('edit_score.html', form=form, score=score)

@app.route('/scores/<int:score_id>/delete')
@login_required
@admin_required
def delete_score(score_id):
    score = Score.query.get_or_404(score_id)
    
    # Users can only delete their own scores, admins can delete any
    if current_user.role != 'admin' and score.created_by != current_user.id:
        abort(403)
    
    db.session.delete(score)
    db.session.commit()
    flash('Score deleted successfully!', 'success')
    return redirect(url_for('scores'))

@app.route('/admin/reset-scores', methods=['POST'])
@login_required
@admin_required
def reset_scores():
    """Reset all scores - Admin only"""
    try:
        # Delete all scores
        Score.query.delete()
        db.session.commit()
        flash('All scores have been reset successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error resetting scores. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/api/leaderboard')
def api_leaderboard():
    teams = Team.query.all()
    leaderboard = []
    
    for team in teams:
        total_score = sum(score.score for score in team.scores)
        leaderboard.append({
            'id': team.id,
            'name': team.name,
            'image_filename': team.image_filename,
            'total_score': total_score,
            'activities_completed': len(team.scores)
        })
    
    # Sort by total score (descending)
    leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
    
    return jsonify(leaderboard)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle_role')
@login_required
@admin_required
def toggle_user_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own role!', 'error')
    else:
        user.role = 'admin' if user.role == 'user' else 'user'
        db.session.commit()
        flash(f'User {user.username} role changed to {user.role}', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} deleted successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/download/sample-teams-csv')
def download_sample_csv():
    """Download sample CSV template for team bulk upload"""
    try:
        csv_content = """Team Name
Team Alpha
Team Beta
Team Gamma
Team Delta
Team Echo
Team Foxtrot
Team Golf
Team Hotel"""
        
        return csv_content, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=sample_teams.csv'
        }
    except Exception as e:
        flash('Error generating sample CSV file.', 'error')
        return redirect(url_for('teams'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', email='admin@scoresheet.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")
    
    # Only run the development server if not on PythonAnywhere
    if not os.environ.get('PYTHONANYWHERE_SITE'):
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Running on PythonAnywhere - use WSGI configuration")
