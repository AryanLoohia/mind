from flask import request, render_template, redirect, url_for, session, flash, jsonify
from . import assessment_bp
from reg.models import db, User, Assessment
from ..forms import AssessmentForm
from ..utils import call_openai_api, extract_score_from_response, handle_api_error, save_assessment_data, has_completed_assessment

REQUIRED_FIELDS = ['question1', 'question2']  # Add all required questions here

@assessment_bp.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    form = AssessmentForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = request.form['name']
        phone = request.form['phone']
        gender = request.form.get('gender')
        answers = {key: value for key, value in request.form.items() if key not in ['name', 'phone', 'gender', 'csrf_token']}
        if not all(field in answers for field in REQUIRED_FIELDS):
            flash('Please answer all questions.', 'danger')
            return redirect(url_for('assessment.assessment'))

        response, error = call_openai_api(answers)
        
        # Save user data regardless of API call result
        save_assessment_data(session['user_id'], name, phone, gender, answers, 0 if error else None)

        if error:
            handle_api_error(error, answers)
            return redirect(url_for('assessment.results', score=0, message='Error processing assessment.'))

        try:
            score = extract_score_from_response(response)
            save_assessment_data(session['user_id'], name, phone, gender, answers, score)
            return redirect(url_for('assessment.results', score=score))
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error processing assessment score: {e}")
            flash('There was an error processing your assessment. Please try again.', 'danger')
            return redirect(url_for('assessment.assessment'))

    return render_template('assessment.html', form=form)

@assessment_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    assessments = Assessment.query.filter_by(user_id=user_id).all()

    try:
        filename = f'user_data/user_{user_id}.json'
        with open(filename, 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}

    return render_template('dashboard.html', user=user, assessments=assessments, user_data=user_data)

@assessment_bp.route('/results')
def results():
    score = request.args.get('score', 0, type=int)
    message = request.args.get('message', '', type=str)
    return render_template('results.html', score=score, message=message)

@assessment_bp.route('/api/user_data')
def user_data():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_id = session['user_id']
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "name": user.name,
        "phone": user.phone,
        "gender": user.gender
    }

    return jsonify(user_data)
