from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, User, Assignment
import os
import csv
import urllib
from uuid import uuid1
import bcrypt
from app import app
from datetime import datetime
from dotenv import load_dotenv

# load environment variables
load_dotenv()
# Database configuration
# db_password = urllib.parse.quote(os.environ.get('db_password'))
db_password = urllib.parse.quote(os.getenv('db_password'))
DATABASE_URL = f"mysql+pymysql://{os.getenv('db_user')}:{db_password}@{os.getenv('db_host')}"
print(DATABASE_URL)
database = create_engine(DATABASE_URL)

# Connect to the MySQL server and create the database.
database.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('db_name')}")

connection_string = f"mysql+pymysql://{os.getenv('db_user')}:{db_password}@{os.getenv('db_host')}/{os.getenv('db_name')}"
engine = create_engine(connection_string)

# Create tables if they don't exist, or update the schema if needed
Base.metadata.create_all(engine, checkfirst=True)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# bcrypt = Bcrypt(app)

# create users from the csv
with open('opt/user.csv', 'r') as csvfile:

    csvreader = csv.DictReader(csvfile)

    # if csvreader.fieldnames is not None:
    #         print("Header row:", csvreader.fieldnames)

    for row in csvreader:

        # if set(csvreader.fieldnames).issubset(row.keys()):
        #     print("Row data:", row)
        # else:
        #     print("Missing columns in row:", row)

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
                            deadline=parsed_date, assignment_created=datetime.now(), assignment_updated=datetime.now(), owner=request_auth)
    print(assignment)
    session.add(assignment)
    session.commit()

    assignment_data = {
            'id': assignment.id,
            'name': assignment.name,
            'points': assignment.points,
            'num_of_attempts':assignment.num_of_attempts,
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


def get_all_assignments_db():
    assignments = session.query(Assignment).all()
    
    assignment_list = []
    for assignment in assignments:
        assignment_data = {
            'id': assignment.id,
            'name': assignment.name,
            'points': assignment.points,
            'num_of_attempts':assignment.num_of_attempts,
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
            'num_of_attempts':assignment.num_of_attempts,
            'deadline': assignment.deadline,
            'assignment_created': assignment.assignment_created.isoformat(),
            'assignment_updated': assignment.assignment_updated.isoformat(),
        }
    
    return assignment_data

# Close the session
session.close()
