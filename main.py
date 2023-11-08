from app import app
from flask import request, redirect, Response
import service
from logging_config import logger
from statsd_config import handle_metric_count


# handles the API requests redirection
@app.route('/', methods=['GET'])
def healthz_redirect():
    if (request.data or request.args):
        logger.error("Method Not Allowed (Request body, query params or path params not allowed)")
        handle_metric_count("failed_400") 
        return service.prepare_response(400)
    
    logger.info("Re-directing to Assignments page")
    return redirect('/v1/assignments')

# handles the API requests for GET method
@app.route('/healthz', methods=['GET'])
def health_check():

    if (request.data or request.args):
        logger.error("Method Not Allowed (Request body, query params or path params not allowed)")
        handle_metric_count("failed_400") 
        return service.prepare_response(400)
    else:
        if service.check_database_connection():
            logger.info("Successful Database Connection")
            handle_metric_count("success_200") 
            return service.prepare_response(200)
        else:
            logger.error("Service Unavailable (Database Connection Refused)")
            handle_metric_count("failed_503") 
            return service.prepare_response(503)


# handles the restricted methods for the API
@app.route('/healthz', methods=['POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD'])
def handle_methods():
    logger.error("Method Not Allowed (Only GET method is allowed)")
    handle_metric_count("failed_405")
    return service.prepare_response(405)


# handles the error when the requested page is not available
@app.errorhandler(404)
def showMessage(error=None):
    logger.error("Not Found (Please check the URL)")
    handle_metric_count("failed_404")
    return service.prepare_response(404)


# handles the error when service is unavailable
@app.errorhandler(500)
def showMessage(error=None):
    logger.error("Service Unavailable (Unexpected error)")
    handle_metric_count("failed_503")
    return service.prepare_response(503)


# handles assignment creation
@app.route('/v1/assignments', methods=['POST'])
def handle_create_assignment():
    
    try:
        auth = request.authorization
        logger.info("Auth Input: ")
        logger.debug(auth)
        if not auth:
            logger.error("Unauthorised (Enter credentials)")
            handle_metric_count("failed_401")
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    except ValueError:
        logger.error("Invalid Authorization header format")
        handle_metric_count("failed_400")
        return service.prepare_response(400)

    logger.info("Inside Create Assignment Method")
    logger.debug("Authorisation Header: " + request.headers.get('Authorization'))

    if (service.check_creds(auth)):
        request_data = request.get_json()
        mandatory_fields = ['name', 'points', 'num_of_attempts', 'deadline']

        if not service.validate_mandatory_fields(request_data, mandatory_fields):
            logger.error("Mandatory fields missing")
            handle_metric_count("failed_400")
            return service.prepare_response(400)

        assignment_data = service.create_assignment(
            auth, request_data)

        if (assignment_data):
            logger.info("Assignment Created Successfully")
            handle_metric_count("success_201")
            return service.prepare_assignments_response(201, assignment_data)
        else:
            logger.error("Bad Request, check values for points and num_of_attempts fields")
            handle_metric_count("failed_400")
            return service.prepare_response(400)
    else:
        logger.error("Unauthorised, check credentials")
        handle_metric_count("failed_401")
        return service.prepare_response(401)


# handles assignment updates
@app.route('/v1/assignments/<assignment_id>', methods=['PUT'])
def handle_update_assignment(assignment_id):
        
    try:
        auth = request.authorization
        if not auth:
            logger.error("Unauthorised, enter Auth values")
            handle_metric_count("failed_401")
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    except ValueError:
        logger.error("Invalid Authorization header format")
        handle_metric_count("failed_400")
        return service.prepare_response(400)

    logger.info("Inside Update Assignment Method")
    logger.debug("Authorisation Header: " + request.headers.get('Authorization'))

    if (service.check_creds(auth)):
        if (service.check_owner(assignment_id, auth) == "Match"):

            request_data = request.get_json()
            mandatory_fields = ['name', 'points',
                                'num_of_attempts', 'deadline']

            if not service.validate_mandatory_fields(request_data, mandatory_fields):
                logger.error("Bad Request, Mandatory Fields Missing")
                handle_metric_count("failed_400")
                return service.prepare_response(400)

            assignment_data = service.update_assignment(
                assignment_id, request.get_json())
            if assignment_data:
                logger.info("Assignment Updated Successfully")
                handle_metric_count("success_204")
                return service.prepare_response(204)
            else:
                logger.error("Bad Request, check values for points and num_of_attempts fields")
                handle_metric_count("failed_400")
                return service.prepare_response(400)
        elif (service.check_owner(assignment_id, auth) == "No Match"):
            logger.error("Forbidden, check credentials")
            handle_metric_count("failed_403")
            return service.prepare_response(403)
        else:
            logger.error("Assignment not found for update")
            handle_metric_count("failed_404")
            return service.prepare_response(404)
    else:
        logger.error("Unauthorised, check credentials")
        handle_metric_count("failed_401")
        return service.prepare_response(401)


# handles delete assignments
@app.route('/v1/assignments/<assignment_id>', methods=['DELETE'])
def handle_delete_assignment(assignment_id):
    
    try:
        auth = request.authorization
        if not auth:
            logger.error("Unauthorised, enter Auth values")
            handle_metric_count("failed_401")
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    except ValueError:
        logger.error("Invalid Authorization header format")
        handle_metric_count("failed_400")
        return service.prepare_response(400)

    logger.info("Inside Delete Assignment Method")
    logger.debug("Authorisation Header: " + request.headers.get('Authorization'))

    if (service.check_creds(auth)):
        if (service.check_owner(assignment_id, auth) == "Match"):
            if (service.delete_assignment(assignment_id)):
                logger.info("Assignment Deleted Successfully")
                handle_metric_count("success_204")
                return service.prepare_response(204)
        elif (service.check_owner(assignment_id, auth) == "No Match"):
            logger.error("Forbidden, check credentials")
            handle_metric_count("failed_403")
            return service.prepare_response(403)
        else:
            logger.error("Assignment not found for deletion")
            handle_metric_count("failed_404")
            return service.prepare_response(404)
    else:
        logger.error("Unauthorised, check credentials")
        handle_metric_count("failed_401")
        return service.prepare_response(401)


# handles get all assignments
@app.route('/v1/assignments', methods=['GET'])
def handle_get_all_assignments():
    
    try:
        auth = request.authorization
        if not auth:
            logger.error("Unauthorised, enter Auth values")
            handle_metric_count("failed_401")
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    except ValueError:
            logger.error("Invalid Authorization header format")
            handle_metric_count("failed_400")
            return service.prepare_response(400)

    logger.info("Inside Get All Assignment Method")
    logger.debug("Authorisation Header: " + request.headers.get('Authorization'))

    if (request.data or request.args):
        logger.error("Method Not Allowed (Request body, query params or path params not allowed)")
        handle_metric_count("failed_400")
        return service.prepare_response(400)
    else:

        if (service.check_creds(auth)):
            # print("inside get all assignments method")
            assignment_list = service.get_all_assignment()
            logger.info("Success All Assignments retrieved")
            handle_metric_count("success_200")
            return service.prepare_assignments_response(200, assignment_list)
        else:
            logger.error("Unauthorised, check credentials")
            handle_metric_count("failed_401")
            return service.prepare_response(401)


@app.route('/v1/assignments/<assignment_id>', methods=['GET'])
def handle_get_by_id_assignment(assignment_id):
    
    try:
        auth = request.authorization
        if not auth:
            logger.error("Unauthorised, enter Auth values")
            handle_metric_count("failed_401")
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    except ValueError:
        logger.error("Invalid Authorization header format")
        handle_metric_count("failed_400")
        return service.prepare_response(400)
    
    logger.info("Inside Get Assignment by ID Method")
    logger.debug("Authorisation Header: " + request.headers.get('Authorization'))

    if (service.check_creds(auth)):
        if (service.check_owner(assignment_id, auth) == "Match"):
            assignment_data = service.get_assignment_by_id(assignment_id)
            logger.info("Assignment retrieved")
            handle_metric_count("success_200")
            return service.prepare_assignments_response(200, assignment_data)
        elif (service.check_owner(assignment_id, auth) == "No Match"):
            logger.error("Forbidden, check credentials")
            handle_metric_count("failed_403")
            return service.prepare_response(403)
        else:
            logger.error("Assignnment not found")
            handle_metric_count("failed_404")
            return service.prepare_response(404)
    else:
        logger.error("Unauthorised, check credentials")
        handle_metric_count("failed_401")
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
