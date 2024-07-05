@echo off

REM Install required Python packages
pip install --upgrade Flask-SQLAlchemy
pip install flask_sqlalchemy==3.0.0
pip install python-dotenv==0.19.2
pip install openai==0.12.17
pip install gunicorn==20.1.0

REM Set environment variables (replace values with your actual values)
set SECRET_KEY=your_secret_key
set SQLALCHEMY_DATABASE_URI=your_database_uri
set OPENAI_API_KEY=your_openai_api_key

REM Run the Flask application
python app.py
