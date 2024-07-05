from flask import request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp
from reg.models import db, User
from ..forms import RegistrationForm, LoginForm
from ..utils import has_completed_assessment

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.redirect_user'))
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if has_completed_assessment(user.id):
                return redirect(url_for('assessment.dashboard'))
            else:
                return redirect(url_for('assessment.assessment'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/redirect_user')
def redirect_user():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session.get('user_id')
    if has_completed_assessment(user_id):
        return redirect(url_for('assessment.dashboard'))
    else:
        return redirect(url_for('assessment.assessment'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))
