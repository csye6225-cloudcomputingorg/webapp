from config import mysql
from flask import jsonify
import bootstrap
import base64
import bcrypt


# function to check the database connectivity
def check_database_connection():
    try:
        bootstrap.check_database_connection
        print("Database connection successful")
        return True
    except Exception as e:
        print("Database connection failed", e)
        return False


# fuction to prepare the response structure of the API
def prepare_response(status_code):
    response = jsonify()
    response.data = b''
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Type'] = 'application/json'
    response.headers['Connection'] = 'keep-alive'

    response.status_code = status_code

    return response


def check_creds(base64_encoded_credentials):
    print("inside check_creds method")
    decoded_credentials = base64.b64decode(
        base64_encoded_credentials).decode("utf-8")
    email, password = decoded_credentials.split(":")
    encoded_password = bootstrap.fetch_password(email)
    print(password.encode('utf-8'))
    print(encoded_password)
    if bcrypt.checkpw(password.encode('utf-8'), encoded_password):
        return True
    else:
        return False


def validate_mandatory_fields(request_data, mandatory_fields):
    for field in mandatory_fields:
        if field not in request_data:
            return False
    return True


def create_assignment(request_auth, request_body):

    print(request_auth, request_body)


    if ((1 <= request_body['points'] <= 10) and (1 <= request_body['num_of_attempts'] <= 3)):
        assignment = bootstrap.create_assignment_db(request_auth, request_body)
        print(assignment)
        return assignment
    else:
        return False


def check_owner(assignment_id, base64_encoded_credentials):
    owner = bootstrap.fetch_owner(assignment_id)
    if owner:
        if owner == base64_encoded_credentials:
            return "Match"
        else:
            return "No Match"
    else:
        return "Not Found"


def update_assignment(assignment_id, request_body):
    print(request_body)

    if ((1 <= request_body['points'] <= 10) and (1 <= request_body['num_of_attempts'] <= 3)):
        assignment = bootstrap.update_assignment_db(assignment_id, request_body)
        print(assignment)
        return assignment
    else:
        return False

def delete_assignment(assignment_id):
    print(assignment_id)
    if(bootstrap.delete_assignment_db(assignment_id)):
        return True
    else:
        return False


def get_all_assignment():
    assigment_list = bootstrap.get_all_assignments_db()
    print(assigment_list)
    return assigment_list


def get_assignment_by_id(assignment_id):
    assignment = bootstrap.get_assignment_by_id_db(assignment_id)
    print(assignment)
    return assignment


def prepare_assignments_response(status_code, assignment_list):
    response = jsonify(assignment_list)
    
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    response.headers['Connection'] = 'keep-alive'

    # response.headers['Access-control-allow-credentials'] = 'true'
    # response.headers['Access-control-allow-headers'] = 'X-Requested-With,Content-Type,Accept,Origin'
    # response.headers['Access-control-allow-methods'] = 'true'
    # response.headers['Access-control-allow-credentials'] = '*' 
    # response.headers['Content-encoding'] = 'gzip'
    # response.headers['X-firefox-spdy'] = 'h2'
  
    response.status_code = status_code
    
    return response
###################### test cases ######################


# def test_get_case():
#     url = 'http://127.0.0.1:5000/healthz'
#     response_get = requests.get(url)
#     response_post = requests.post(url)
#     response_not_found = requests.get(url+'/')
#     assert response_get.status_code == 200
#     assert response_post.status_code == 405
#     assert response_not_found.status_code == 404


# def test_post_case():
#     response_post = app.test_client().post('/healthz')
#     assert response_post.status_code == 405


# def test_not_found_case():
#     response_not_found = app.test_client().get('/healthz/')
#     assert response_not_found.status_code == 404
###################### test cases ######################
