from app import app
from flask import request
import service
# from config import set_db_creds
from bootstrap import engine

# handles the API requests for GET method


@app.route('/healthz', methods=['GET'])
def health_check():

    if (request.data or request.args):
        print("Method Not Allowed")
        return service.prepare_response(400)
    else:
 #       set_db_creds()
        if service.check_database_connection():
            print("Success")
            return service.prepare_response(200)
        else:
            print("Service Unavailable")
            return service.prepare_response(503)


# handles the restricted methods for the API
@app.route('/healthz', methods=['POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD'])
def handle_methods():
    print("Method Not Allowed")
    return service.prepare_response(405)


# handles the error when the requested page is not available
@app.errorhandler(404)
def showMessage(error=None):
    print("Not Found")
    return service.prepare_response(404)


# handles the error when service is unavailable
@app.errorhandler(500)
def showMessage(error=None):
    print("Service Unavailable")
    return service.prepare_response(503)


# handles assignment creation
@app.route('/v1/assignments', methods=['POST'])
def handle_create_assignment():
    print("inside post method")
    print(request.headers.get('Authorization'))
    try:
        _, base64_encoded_credentials = request.headers.get(
            'Authorization').split(" ", 1)
        print(base64_encoded_credentials)
    except ValueError:
        print("Invalid Authorization header format")
        base64_encoded_credentials = None

    if (service.check_creds(base64_encoded_credentials)):
        request_data = request.get_json()
        mandatory_fields = ['name', 'points', 'num_of_attempts', 'deadline']

        if not service.validate_mandatory_fields(request_data, mandatory_fields):
            return service.prepare_response(400)

        assignment_data = service.create_assignment(
            base64_encoded_credentials, request_data)

        if(assignment_data):
            return service.prepare_assignments_response(201, assignment_data)
        else:
            return service.prepare_response(400)
    else:
        return service.prepare_response(401)


# handles assignment updates
@app.route('/v1/assignments/<assignment_id>', methods=['PUT'])
def handle_update_assignment(assignment_id):
    print("inside put method")
    print(request.headers.get('Authorization'))
    try:
        _, base64_encoded_credentials = request.headers.get(
            'Authorization').split(" ", 1)
        print(base64_encoded_credentials)
    except ValueError:
        print("Invalid Authorization header format")
        base64_encoded_credentials = None

    if (service.check_creds(base64_encoded_credentials)):
        if(service.check_owner(assignment_id, base64_encoded_credentials) == "Match"):

            request_data = request.get_json()
            mandatory_fields = ['name', 'points',
                                'num_of_attempts', 'deadline']

            if not service.validate_mandatory_fields(request_data, mandatory_fields):
                return service.prepare_response(400)

            assignment_data = service.update_assignment(assignment_id, request.get_json())
            if assignment_data:
                return service.prepare_response(204)
            else:
                return service.prepare_response(400)
        elif (service.check_owner(assignment_id, base64_encoded_credentials) == "No Match"):
            return service.prepare_response(403)
        else:
            return service.prepare_response(404)
    else:
        return service.prepare_response(401)


# handles delete assignments
@app.route('/v1/assignments/<assignment_id>', methods=['DELETE'])
def handle_delete_assignment(assignment_id):
    print("inside delete method")
    print(request.headers.get('Authorization'))
    try:
        _, base64_encoded_credentials = request.headers.get(
            'Authorization').split(" ", 1)
        print(base64_encoded_credentials)
    except ValueError:
        print("Invalid Authorization header format")
        base64_encoded_credentials = None

    if (service.check_creds(base64_encoded_credentials)):
        if(service.check_owner(assignment_id, base64_encoded_credentials) == "Match"):
            if(service.delete_assignment(assignment_id)):
                return service.prepare_response(204)
        elif (service.check_owner(assignment_id, base64_encoded_credentials) == "No Match"):
            return service.prepare_response(403)
        else:
            return service.prepare_response(404)
    else:
        return service.prepare_response(401)


# handles get all assignments
@app.route('/v1/assignments', methods=['GET'])
def handle_get_all_assignments():

    if (request.data or request.args):
        print("Method Not Allowed")
        return service.prepare_response(400)
    else:
        try:
            _, base64_encoded_credentials = request.headers.get(
                'Authorization').split(" ", 1)
            print(base64_encoded_credentials)
        except ValueError:
            print("Invalid Authorization header format")
            base64_encoded_credentials = None

        if (service.check_creds(base64_encoded_credentials)):
            print("inside get all assignments method")
            assignment_list = service.get_all_assignment()
            return service.prepare_assignments_response(200, assignment_list)
        else:
            return service.prepare_response(401)


@app.route('/v1/assignments/<assignment_id>', methods=['GET'])
def handle_get_by_id_assignment(assignment_id):
    print("inside get by id method")
    print(request.headers.get('Authorization'))
    try:
        _, base64_encoded_credentials = request.headers.get(
            'Authorization').split(" ", 1)
        print(base64_encoded_credentials)
    except ValueError:
        print("Invalid Authorization header format")
        base64_encoded_credentials = None

    if (service.check_creds(base64_encoded_credentials)):
        if(service.check_owner(assignment_id, base64_encoded_credentials)=="Match"):
            assignment_data = service.get_assignment_by_id(assignment_id)
            return service.prepare_assignments_response(200, assignment_data)
        elif (service.check_owner(assignment_id, base64_encoded_credentials)=="No Match"):
            return service.prepare_response(403)
        else:
            return service.prepare_response(404)
    else:
        return service.prepare_response(401)


# run test cases
# service.test_get_case()
# service.test_post_case()
# service.test_not_found_case()


# main method
if __name__ == "__main__":
    # with engine.connect() as connection:
    #    connection.execute("SELECT 1")
    app.run(host='0.0.0.0', port=3001)
