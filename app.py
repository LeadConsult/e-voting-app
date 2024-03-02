from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import random
import string
from datetime import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'

db = SQLAlchemy(app)

# Define models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    matric = db.Column(db.String(10), unique=True, nullable=False)
    level = db.Column(db.String(10), nullable=False)
    token = db.Column(db.String(50))
    accredited = db.Column(db.String(50))
    voted = db.Column(db.String(50))

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), nullable=False)
    pres = db.Column(db.String(100), nullable=True)
    vp = db.Column(db.String(100), nullable=True)
    sec = db.Column(db.String(100), nullable=True)
    fsec = db.Column(db.String(100), nullable=True)
    tre = db.Column(db.String(100), nullable=True)
    sport = db.Column(db.String(100), nullable=True)
    social = db.Column(db.String(100), nullable=True)
    lib = db.Column(db.String(100), nullable=True)
    timestamp_voted = db.Column(db.String(100), nullable=True)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/verify_token', methods=['GET', 'POST'])
def verify_token():
    if request.method == 'POST':
        token = request.form.get('token')
        student = Student.query.filter_by(token=token).first()
        votes = Votes.query.filter_by(token=token).first()
        if student:
            return render_template('verify_token.html', student=student, votes=votes)
        else:
            return render_template('verify_token.html', error='Token number does not exist.')
    else:
        return render_template('verify_token.html')

@app.route('/submit_student', methods=['GET', 'POST'])
def submit_student():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '')
            matric = request.form.get('matric', '')
            level = request.form.get('level', '')

            # Create a new student object
            new_student = Student(name=name, matric=matric, level=level, accredited="No", voted="No", token="")

            # Add the student to the database
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('add_student_success'))
        except IntegrityError as e:
            # Handle integrity constraint violation (e.g., duplicate matric number)
            db.session.rollback()  # Rollback the transaction
            db.session.expunge_all()
            print(e)  # Print the exception for debugging
            error = 'Matric number already exists.'
            return render_template('add_student.html', error=error)
            
        except Exception as e:
            # Handle other exceptions
            print(e)  # Print the exception for debugging
            error = 'An error occurred while adding the student. Please try again.'
            return render_template('add_student.html', error=error)
    
    return render_template('add_student.html')

# Generate a unique token consisting of numbers only
def generate_unique_token():
    while True:
        new_token = ''.join(random.choices(string.digits, k=6))
        if not Student.query.filter_by(token=new_token).first():
            return new_token

# Flask route to render verify.html and handle matric verification
@app.route('/verify', methods=['GET', 'POST'])
def verify_matric():
    if request.method == 'POST':
        matric = request.form.get('matric')
        student = Student.query.filter_by(matric=matric).first()
        if student:
            if student.accredited == 'No':  # Check if student is not already accredited
                # Generate token, fetch name and level, update accreditation status
                student.token = generate_unique_token()
                student.accredited = 'Yes'
                db.session.commit()
                return render_template('verify.html', student=student)
            else:
                if student.voted == 'Yes': 
                    error = 'Student is already accredited and Voted.'
                else:
                    error = 'Student is already accredited.'
                    
                # Student is already accredited, prevent regeneration of token
                return render_template('verify.html', error=error, student=student)
        else:
            return render_template('verify.html', error='Matric number does not exist.')
    else:
        # Render the verify.html template
        return render_template('verify.html')

# Route for the success page after adding a student
@app.route('/add_student_success')
def add_student_success():
    added = "Student added successfully!"
    return render_template('add_student.html', added=added)

@app.route('/login', methods=['GET', 'POST'])
def login():
    token = request.args.get('token')  # Get the token from the query parameters
    if token:
        # Check if the token exists in the votes table
        existing_vote = Votes.query.filter_by(token=token).first()
        if existing_vote:
            error = "You have already voted!"
            return render_template('login.html', error=error)
        else:
            # Check if the token exists and the student is accredited
            student = Student.query.filter_by(token=token, accredited='Yes', voted='No').first()
            student_voted = Student.query.filter_by(token=token, accredited='Yes', voted='Yes').first()
            if student:
                # If the token exists and the student is accredited, redirect to vote.html
                return render_template('vote.html', token=token)
            
            elif student_voted:
                 error = "Token already used for voting!"
                 return render_template('login.html', error=error)
            
            else:
                error = "Token not found!"
                return render_template('login.html', error=error)
    # If token doesn't exist, render login.html
    return render_template('login.html')

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    # Retrieve the selected candidates from the form
    presidential_candidate = request.form.get('presidential_candidate')
    vice_presidential_candidate = request.form.get('vice_presidential_candidate')
    secretary_candidate = request.form.get('secretary_candidate')
    financial_secretary_candidate = request.form.get('financial_secretary_candidate')
    treasurer_candidate = request.form.get('treasurer_candidate')
    sports_secretary_candidate = request.form.get('sports_secretary_candidate')
    social_secretary_candidate = request.form.get('social_secretary_candidate')
    librarian_candidate = request.form.get('librarian_candidate')
    token = request.form.get('token')
    timestamp_voted = datetime.now()
    
     # Create a new Votes record
    new_votes = Votes(
        token=token,
        pres=presidential_candidate,
        vp=vice_presidential_candidate,
        sec=secretary_candidate,
        fsec=financial_secretary_candidate,
        tre=treasurer_candidate,
        sport=sports_secretary_candidate,
        social=social_secretary_candidate,
        lib=librarian_candidate,
        timestamp_voted=timestamp_voted
    )

    # Add the Votes record to the database
    db.session.add(new_votes)
    db.session.commit()
    
     # Update the student's voted status to 'Yes'
    student = Student.query.filter_by(token=token).first()
    if student:
        student.voted = 'Yes'
        db.session.commit()

    # Redirect to a thank you page or render a template
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('thank_you.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
