from config import mysql
from flask import jsonify, Response
import bootstrap
from datetime import datetime
import bcrypt
from logging_config import logger
from statsd_config import handle_metric_count
import boto3
import re
import requests
import os


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


# function to check the database connectivity
def check_database_connection():
    try:
        bootstrap.check_database_connection
        print("Database connection successful")
        return True
    except Exception as e:
        print("Database connection failed", e)
        return False


def check_authorization(request, logger_statement):
    try:
        auth = request.authorization
        logger.info("Auth Input: ")
        logger.debug(auth)
        if not auth:
            logger.error("Unauthorised (Enter credentials)")
            handle_metric_count("failed_401")
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        else:
            return auth
    except ValueError:
        logger.error("Invalid Authorization header format")
        handle_metric_count("failed_400")
        return prepare_response(400)

    logger.info(logger_statement)
    logger.debug("Authorisation Header: " +
                 request.headers.get('Authorization'))


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


def check_creds(auth):
    print("inside check_creds method")

    encoded_password = bootstrap.fetch_password(auth.username)
    print(auth.password.encode('utf-8'))
    print(encoded_password)
    if bcrypt.checkpw(auth.password.encode('utf-8'), encoded_password):
        return True
    else:
        return False


def validate_mandatory_fields(request_data, mandatory_fields):
    for field in mandatory_fields:
        if field not in request_data:
            return False
    return True


def validate_request(request_data, mandatory_fields):
    isValid = True

    isValid = False if len(request_data.keys()) != 4 else True

    for field in mandatory_fields:
        if field not in request_data:
            isValid = False

    for value in request_data.values():
        if value is None:
            isValid = False

    isValid = False if 'name' in request_data and not isinstance(
        request_data['name'], str) else True

    if 'num_of_attempts' in request_data and request_data['num_of_attempts'] is not None:
        try:
            num_attempts = int(request_data['num_of_attempts'])

            if num_attempts != float(request_data['num_of_attempts']):
                isValid = False
                logger.warn(
                    f"Warning: The value for num_of_attempts is not a valid integer ({request_data['num_of_attempts']}).")
            else:
                request_data['num_of_attempts'] = num_attempts
        except ValueError:
            isValid = False
            logger.warn(
                f"Warning: The value for num_of_attempts is not a valid integer ({request_data['num_of_attempts']}).")

    try:
        datetime.strptime(request_data['deadline'], '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        isValid = False

    return isValid


def create_assignment(request_auth, request_body):

    print(request_auth, request_body)

    if ((1 <= request_body['points'] <= 10) and (1 <= request_body['num_of_attempts'] <= 3)):
        assignment = bootstrap.create_assignment_db(request_auth, request_body)
        print(assignment)
        return assignment
    else:
        return False


def check_owner(assignment_id, auth):
    owner = bootstrap.fetch_owner(assignment_id)
    if owner:
        if owner == auth.username:
            return "Match"
        else:
            return "No Match"
    else:
        return "Not Found"


def update_assignment(assignment_id, request_body):
    print(request_body)

    if ((1 <= request_body['points'] <= 10) and (1 <= request_body['num_of_attempts'] <= 3)):
        assignment = bootstrap.update_assignment_db(
            assignment_id, request_body)
        print(assignment)
        return assignment
    else:
        return False


def delete_assignment(assignment_id):
    print(assignment_id)
    if (bootstrap.delete_assignment_db(assignment_id)):
        return True
    else:
        return False


def get_all_assignment():
    assigment_list = bootstrap.get_all_assignments_db()
    print(assigment_list)
    return assigment_list


def get_assignment_by_id(auth, assignment_id):

    if (check_creds(auth)):
        if (check_owner(assignment_id, auth) == "Match"):
            assignment_data = bootstrap.get_assignment_by_id_db(assignment_id)
            print(assignment_data)
            logger.info("Assignment retrieved")
            handle_metric_count("success_200")
            return prepare_assignments_response(200, assignment_data)
        elif (check_owner(assignment_id, auth) == "No Match"):
            logger.error("Forbidden, check credentials")
            handle_metric_count("failed_403")
            return prepare_response(403)
        else:
            logger.error("Assignnment not found")
            handle_metric_count("failed_404")
            return prepare_response(404)
    else:
        logger.error("Unauthorised, check credentials")
        handle_metric_count("failed_401")
        return prepare_response(401)


def submit_assignment(auth, response, request):
    request_data = request.get_json()

    pattern = re.compile(
        r'^https://github\.com/[\w-]+/[\w-]+/archive/refs/tags/v\d+\.\d+\.\d+\.zip$')

    assignment_id = response.get_json()['id']
    num_of_attempts = response.get_json()['num_of_attempts']
    deadline = datetime.strptime(
        response.get_json()['deadline'], '%Y-%m-%d %H:%M:%S.%f')
    if len(request_data.keys()) == 1 and 'submission_url' in request_data and request_data['submission_url'] is not None:
        submission_url = request_data['submission_url']
        match = pattern.match(submission_url)

        if match:
            if deadline > datetime.now():
                id, status = bootstrap.update_assignment_submission_count(
                    assignment_id, num_of_attempts)

                assignment_data = {
                    'id': id,
                    'assignment_id': assignment_id,
                    'submission_url': submission_url,
                    'submission_date': datetime.now(),
                    'submission_updated': datetime.now(),
                }

                print(match)
                if (status == 'submitted'):
                    sns_topic_arn = environment_variables.get("SNS_TOPIC_ARN")
                    user_email = auth.username
                    release_tag = re.search(
                        r'/v([\d.]+)\.zip$', submission_url)
                    repo_url = submission_url.split("/archive")[0]

                    logger.debug(os.environ.get('SNS_TOPIC_ARN'))

                    post_to_sns_topic(sns_topic_arn, user_email, release_tag, repo_url)

                return assignment_data, status
            else:
                logger.error(
                    "The submission deadline has passed. No further submissions are allowed.")
                return 404, "deadlinePassed"
        else:
            logger.error("Invalid Submission URL")
            return 400, "Invalid Submission URL"
    else:
        logger.error("Invalid Request")
        return 400, "Bad Request"


def prepare_assignments_response(status_code, assignment_list):
    response = jsonify(assignment_list)

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    response.headers['Connection'] = 'keep-alive'

    response.status_code = status_code

    return response


def post_to_sns_topic(topic_arn, user_email, release_tag, repo_url):
    sns = boto3.client('sns', region_name='your-region')

    message = {
        'user_email': user_email,
        'release_tag': release_tag,
        'repo_url': repo_url,
    }

    response = sns.publish(
        TopicArn=topic_arn,
        Message=str(message),
        Subject='New Release Notification',
    )

    logger.info(
        f"Message sent to SNS Topic. MessageId: {response['MessageId']}")

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
