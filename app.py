from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import time
import json
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, HiddenField, validators
from flask_migrate import Migrate
from groq import Groq
import uuid
from flask_cors import CORS
from typing import List, Tuple

app = Flask(__name__)
CORS(app)
load_dotenv()

# Critical configuration loading and validation
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
if not app.config['SECRET_KEY'] or not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("Critical environment variables are missing")

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024  # 16 MB max size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

groq_api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)

REQUIRED_FIELDS = ['question1', 'question2']  # Add all required questions here

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=6)
    ])

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class AssessmentForm(FlaskForm):
    csrf_token = HiddenField()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/player', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        # Handle POST request logic here
        pass
    return render_template('player.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        name = request.form.get('name', 'User')  # Default to 'User' if name is not provided
        logger.debug(f"Received registration data: username={username}, name={name}")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password, name=name)
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('register'))

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('redirect_user'))
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if has_completed_assessment(user.id):
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('assessment'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/redirect_user')
def redirect_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    if has_completed_assessment(user_id):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('assessment'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

MAX_RETRY_ATTEMPTS = 1
RETRY_DELAY = 5

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    form = AssessmentForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = request.form['name']
        phone = request.form['phone']
        gender = request.form.get('gender')
        logger.info(f"Received assessment data: name={name}, phone={phone}, gender={gender}")
        answers = {key: value for key, value in request.form.items() if key not in ['name', 'phone', 'gender', 'csrf_token']}
        if not all(field in answers for field in REQUIRED_FIELDS):
            flash('Please answer all questions.', 'danger')
            return redirect(url_for('assessment'))
        
        attempt = 1
        while attempt <= MAX_RETRY_ATTEMPTS:
            try:
                response, error = call_groq_api(answers)
                if error:
                    logger.error(f"Error calling Groq API: {error}")
                    if attempt == MAX_RETRY_ATTEMPTS:
                        handle_api_error(error, answers)
                        return redirect(url_for('results', score=0, message='Error processing assessment.'))
                
                score = extract_score_from_response(response)
                save_assessment_data(session['user_id'], name, phone, gender, answers, score)
                return redirect(url_for('results', score=score))  # Ensure score is defined here

            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"Error processing assessment: {e}")
                attempt += 1
                if attempt <= MAX_RETRY_ATTEMPTS:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    break
        
        # If all attempts failed, save the assessment data with score=0
        save_assessment_data(session['user_id'], name, phone, gender, answers, 0)
        handle_api_error(error, answers)
        return redirect(url_for('results', score=0, message='Error processing assessment.'))
    
    return render_template('assessment.html', form=form)


def call_groq_api(answers):
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        messages = format_messages(answers)
        response = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
        )
        return response, None  # No error
    except Exception as e:
        return None, str(e)  # Return error message

def format_messages(answers):
    # Create a structured prompt for the Groq API
    prompt = " You will act as an expert in mental health to evaluate answers provided by users. Your task is to evaluate the following answers for a mental health assessment on a scale of 1 to 10, where 1 indicates the most chance of mental illness and 10 indicates the least. Here are the answers in multiple-choice format: {answers}. Please respond with an overall rating in number form only.\n"
    for question, answer in answers.items():
        prompt += f"Question: {question}\nAnswer: {answer}\n\n"
    return [{"role": "user", "content": prompt}]

def save_assessment_data(user_id, name, phone, gender, answers, score):
    user = User.query.get(user_id)
    if user:
        user.name = name
        user.phone = phone
        user.gender = gender
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            db.session.rollback()

    new_assessment = Assessment(user_id=user_id, score=score)
    try:
        db.session.add(new_assessment)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error saving assessment data: {e}")
        db.session.rollback()

    user_data = {
        "name": name,
        "phone": phone,
        "gender": gender,
        "answers": answers,
        "score": score
    }
    try:
        if not os.path.exists('user_data'):
            os.makedirs('user_data')
        filename = f'user_data/{name.replace(" ", "_")}_user_{user_id}.json'
        with open(filename, 'w') as f:
            json.dump(user_data, f)
    except Exception as e:
        logger.error(f"Error saving assessment data: {e}")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db.session.get(User, user_id)

    if not user:
        logger.error(f"User with ID {user_id} not found")
        flash('User not found. Please log in again.', 'danger')
        session.clear()
        return redirect(url_for('login'))

    if not user.name:
        flash('Please complete the assessment first.', 'warning')
        return redirect(url_for('assessment'))

    assessments = Assessment.query.filter_by(user_id=user_id).all()

    try:
        user_name = user.name if user.name else "user"
        filename = f'user_data/{user_name.replace(" ", "_")}_user_{user_id}.json'
        with open(filename, 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}

    return render_template('dashboard.html', user=user, assessments=assessments, user_data=user_data)



@app.route('/results', methods=['GET'])
def results():
    score = request.args.get('score', 0, type=int)
    message = request.args.get('message', None)
    return render_template('results.html', score=score, message=message)

def has_completed_assessment(user_id):
    assessment = Assessment.query.filter_by(user_id=user_id).first()
    return assessment is not None

def extract_score_from_response(response):
    try:
        # Check the structure of the response and log it for debugging
        logger.info(f"Groq API response: {response}")
        content = response.choices[0].message.content
        
        # Check if content is a plain integer
        score = int(content.strip())
        return score
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Error extracting score: {e}")
        raise

def handle_api_error(error, answers):
    if not os.path.exists('errors'):
        os.makedirs('errors')
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    error_filename = f'error_{timestamp}.json'
    error_data = {
        'error': str(error),
        'answers': answers
    }
    try:
        with open(os.path.join('errors', error_filename), 'w') as error_file:
            json.dump(error_data, error_file, indent=4)
    except Exception as e:
        logger.error(f"Error saving API error log: {e}")

def has_completed_assessment(user_id):
    return Assessment.query.filter_by(user_id=user_id).count() > 0

@app.route('/api/user_data')
def user_data():
    if 'user_id' not in session:
        logger.warning("User not logged in")
        return jsonify({"error": "User not logged in"}), 401

    user_id = session['user_id']
    user = db.session.get(User, user_id)

    if not user:
        logger.error(f"User with ID {user_id} not found")
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "name": user.name,
        "phone": user.phone,
        "gender": user.gender,
        "username": user.username  # Additional detail if needed
    }

    logger.info(f"Retrieved user data: {user_data}")

    return jsonify(user_data)

@app.route('/api/user_assessments', methods=['GET'])
def user_assessments():
    if 'user_id' not in session:
        logger.warning("User not logged in")
        return jsonify({"error": "User not logged in"}), 401

    user_id = session['user_id']
    assessments = Assessment.query.filter_by(user_id=user_id).all()

    if not assessments:
        logger.error(f"No assessments found for user with ID {user_id}")
        return jsonify({"error": "No assessments found"}), 404

    assessments_data = []
    for assessment in assessments:
        assessment_data = {
            "id": assessment.id,
            "score": assessment.score,
            "timestamp": assessment.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Example timestamp formatting
            # Add more fields as needed
        }
        assessments_data.append(assessment_data)

    logger.info(f"Retrieved assessments data for user {user_id}: {assessments_data}")

    return jsonify(assessments_data)

# Custom error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 error: {e}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 error: {e}")
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
