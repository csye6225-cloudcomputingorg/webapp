from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, User, Assignment, Submission
import os
import csv
import urllib
from uuid import uuid1
import bcrypt
from app import app
from datetime import datetime
from dotenv import load_dotenv
import requests


# Fetch user data
user_data_url = "http://169.254.169.254/latest/user-data"
response = requests.get(user_data_url)
user_data = response.text

# Split user data into lines
lines = user_data.split('\n')

# Parse environment variable assignments
environment_variables = {}
for line in lines:
    if line.strip().startswith("export "):
        parts = line.strip()[7:].split("=")
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            environment_variables[key] = value

# Access the environment variables
db_host = environment_variables.get("DB_HOST")
db_name = environment_variables.get("DB_NAME")
db_user = environment_variables.get("DB_USER")
db_password = environment_variables.get("DB_PASSWORD")

# db_password = urllib.parse.quote('Cloud@2023')
# DATABASE_URL = f"mysql+pymysql://csye6225:{db_password}@localhost/csye6225cloudcomputing"

# load environment variables
DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}"
print(DATABASE_URL)
database = create_engine(DATABASE_URL)

# connection_string = f"mysql+pymysql://csye6225:{db_password}@localhost/csye6225cloudcomputing"

connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
print(connection_string)

engine = create_engine(connection_string)


def check_database_connection():
    return engine.connect()


# Create tables if they don't exist, or update the schema if needed
Base.metadata.create_all(engine, checkfirst=True)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# create users from the csv
with open('/home/admin/webapp/opt/user.csv', 'r') as csvfile:
# with open('opt/user.csv', 'r') as csvfile:

    csvreader = csv.DictReader(csvfile)

    for row in csvreader:

        first_name = row['first_name']
        last_name = row['last_name']
        email = row['email']
        password = row['password']

        # Check if the user already exists in the database based on username or email
        existing_user = session.query(User).filter(User.email == email).first()

        if not existing_user:
            hashed_password = bcrypt.hashpw(
                row['password'].encode('utf-8'), bcrypt.gensalt())
            user = User(first_name=row['first_name'], last_name=row['last_name'], email=row['email'],
                        password=hashed_password, account_created=datetime.now(), account_updated=datetime.now())
            print(user.first_name, user.last_name, user.email, user.password)
            session.add(user)
            session.commit()


def fetch_password(email):
    print("inside fetch password method")
    password = session.query(User).filter(User.email == email).first().password
    print(password)
    return password


def create_assignment_db(request_auth, request_body):

    print("inside create_assignment_db")
    print(request_body['name'], request_body['points'],
          request_body['num_of_attempts'], request_body['deadline'])

    parsed_date = datetime.strptime(
        request_body['deadline'], '%Y-%m-%dT%H:%M:%S.%fZ')
    id = uuid1()
    print(id)
    assignment = Assignment(id=str(id), name=request_body['name'], points=request_body['points'], num_of_attempts=request_body['num_of_attempts'],
                            deadline=parsed_date, assignment_created=datetime.now(), assignment_updated=datetime.now(), owner=request_auth.username, num_of_submission=0)
    print(assignment.owner)
    session.add(assignment)
    session.commit()

    assignment_data = {
        'id': assignment.id,
        'name': assignment.name,
        'points': assignment.points,
        'num_of_attempts': assignment.num_of_attempts,
        'deadline': assignment.deadline,
        'assignment_created': assignment.assignment_created.isoformat(),
        'assignment_updated': assignment.assignment_updated.isoformat(),
    }

    return assignment_data


def fetch_owner(assignment_id):
    try:
        owner = session.query(Assignment).filter(
            Assignment.id == assignment_id).first().owner
        print(owner)
        return owner
    except:
        return False


def update_assignment_db(assignment_id, request_body):
    assignment = session.query(Assignment).filter(
        Assignment.id == assignment_id).first()

    parsed_date = datetime.strptime(
        request_body['deadline'], '%Y-%m-%dT%H:%M:%S.%fZ')

    print(assignment.name)

    assignment.name = request_body['name']
    assignment.points = request_body['points']
    assignment.num_of_attempts = request_body['num_of_attempts']
    assignment.deadline = parsed_date
    assignment.assignment_updated = datetime.now()

    session.commit()

    return True


def delete_assignment_db(assignment_id):
    assignment = session.query(Assignment).filter(
        Assignment.id == assignment_id).first()

    session.delete(assignment)
    session.commit()

    deleted_assignment = session.query(Assignment).get(assignment_id)
    if deleted_assignment is None:
        return True
    else:
        return False


def update_assignment_submission_count(assignment_id, num_of_attempts):
    try:
        assignment = session.query(Assignment).filter(
            Assignment.id == assignment_id).first()

        id = uuid1()

        if (assignment.num_of_submission < num_of_attempts):

            assignment.num_of_submission += 1
            session.commit()
            status = "submitted"
        else:
            status = "exceeded"

        return id, status

    except:
        id = -1,
        status = "failed"
        return id, status


def submit_assignnment(assignment_id, username, submission_url ):
    
    id = uuid1()
    submission = Submission(id=str(id), assignment_id=assignment_id, submission_url=submission_url, user_id=username,
                            submission_date=datetime.now(), submission_updated=datetime.now())
    
    print(submission)
    session.add(submission)
    session.commit()
    
    submission_data = {
                'id': id,
                'assignment_id': assignment_id,
                'submission_url': submission_url,
                'submission_date': datetime.now(),
                'submission_updated': datetime.now(),
            }
    
    return submission_data


def get_all_assignments_db():
    assignments = session.query(Assignment).all()

    assignment_list = []
    for assignment in assignments:
        assignment_data = {
            'id': assignment.id,
            'name': assignment.name,
            'points': assignment.points,
            'num_of_attempts': assignment.num_of_attempts,
            'deadline': assignment.deadline,
            'assignment_created': assignment.assignment_created.isoformat(),
            'assignment_updated': assignment.assignment_updated.isoformat(),
        }
        assignment_list.append(assignment_data)

    return assignment_list


def get_assignment_by_id_db(assignment_id):
    assignment = session.query(Assignment).filter(
        Assignment.id == assignment_id).first()

    assignment_data = {
        'id': assignment.id,
        'name': assignment.name,
        'points': assignment.points,
        'num_of_attempts': assignment.num_of_attempts,
        'deadline': assignment.deadline,
        'assignment_created': assignment.assignment_created.isoformat(),
        'assignment_updated': assignment.assignment_updated.isoformat(),
    }

    return assignment_data


def get_number_of_submissions(username, assignment):
   
    submission_count = session.query(Submission).filter(
        Submission.assignment_id == assignment['id'],
        Submission.user_id == username
    ).count()
    
    if submission_count < assignment['num_of_attempts']:
        return True
    else:
        return False

# Close the session
session.close()
