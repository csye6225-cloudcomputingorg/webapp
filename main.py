from app import app
from flask import request, redirect
import service
from logging_config import logger
from statsd_config import handle_metric_count


# handles the API requests redirection
@app.route('/', methods=['GET'])
def redirect_api():

    auth = service.check_authorization(
        request, "Inside Redirect to Get All Assignment Method")

    if (request.data or request.args):
        logger.error(
            "Method Not Allowed (Request body, query params or path params not allowed)")
        handle_metric_count("failed_400")
        return service.prepare_response(400)
    else:
        if (service.check_creds(auth)):
            logger.info("Re-directing to Assignments page")
            return redirect('/v1/assignments')
        else:
            logger.error("Unauthorised, check credentials")
            handle_metric_count("failed_401")
            return service.prepare_response(401)


# handles the API requests for GET method
@app.route('/healthz', methods=['GET'])
def health_check():

    if (request.data or request.args):
        logger.error(
            "Method Not Allowed (Request body, query params or path params not allowed)")
        handle_metric_count("failed_400")
        return service.prepare_response(400)
    else:
        if service.check_database_connection():
        # if 1:
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


@app.route('/v1/assignments', methods=['PATCH'])
def handle_method():
    logger.error("Method Not Allowed")
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

    auth = service.check_authorization(
        request, "Inside Create Assignment Method")

    if (service.check_creds(auth)):
        request_data = request.get_json()
        mandatory_fields = ['name', 'points', 'num_of_attempts', 'deadline']

        if not service.validate_request(request_data, mandatory_fields):
            logger.error("Mandatory fields missing")
            handle_metric_count("failed_400")
            return service.prepare_response(400)

        assignment_data = service.create_assignment(
            auth, request_data)

        if (assignment_data):
            logger.info("Assignment Created Successfully")
            handle_metric_count("success_201")
            response = service.prepare_assignments_response(201, assignment_data)
            response.status = "201 ASSIGNMENT CREATED"
            return response
        else:
            logger.error(
                "Bad Request, check values for points and num_of_attempts fields")
            handle_metric_count("failed_400")
            return service.prepare_response(400)
    else:
        logger.error("Unauthorised, check credentials")
        handle_metric_count("failed_401")
        return service.prepare_response(401)


# handles assignment updates
@app.route('/v1/assignments/<assignment_id>', methods=['PUT'])
def handle_update_assignment(assignment_id):

    auth = service.check_authorization(
        request, "Inside Update Assignment Method")

    if (service.check_creds(auth)):
        if (service.check_owner(assignment_id, auth) == "Match"):

            request_data = request.get_json()
            mandatory_fields = ['name', 'points',
                                'num_of_attempts', 'deadline']

            if not service.validate_request(request_data, mandatory_fields):
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
                logger.error(
                    "Bad Request, check values for points and num_of_attempts fields")
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

    auth = service.check_authorization(
        request, "Inside Delete Assignment Method")

    if (request.data or request.args):
        logger.error(
            "Method Not Allowed (Request body, query params or path params not allowed)")
        handle_metric_count("failed_400")
        return service.prepare_response(400)
    else:
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

    auth = service.check_authorization(
        request, "Inside Get All Assignment Method")

    if (request.data or request.args):
        logger.error(
            "Method Not Allowed (Request body, query params or path params not allowed)")
        handle_metric_count("failed_400")
        return service.prepare_response(400)
    else:

        if (service.check_creds(auth)):
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

    auth = service.check_authorization(
        request, "Inside Get Assignment by ID Method")

    if (request.data or request.args):
        logger.error(
            "Method Not Allowed (Request body, query params or path params not allowed)")
        handle_metric_count("failed_400")
        return service.prepare_response(400)
    else:
        return service.get_assignment_by_id(auth, assignment_id)

@app.route('/v1/assignments/<assignment_id>/submission', methods=['POST'])
def handle_assignment_submission(assignment_id):

    auth = service.check_authorization(
        request, "Inside Post Assignment Submission Method")

    if (service.check_creds(auth)):
        assignment_response = service.get_assignment_by_id(auth, assignment_id)

        if assignment_response.status_code == 200:
            data, status = service.submit_assignment(auth, response, request)
            if (status == 'submitted'):
                response = service.prepare_assignments_response(201, data)
                response.status = '201 SUBMISSION ACCEPTED'
            elif (status == 'exceeded'):
                response = service.prepare_assignments_response(429, data)
                response.status = '429 SUBMISSION ATTEMPTS EXCEEDED'
            elif (status == 'deadlinePassed'):
                response = service.prepare_response(404)
                response.status = '404 SUBMISSION DEADLINE PASSED'
            else:
                response = service.prepare_response(400)
        elif assignment_response.status_code == 404:
            response = service.prepare_response(404)
            logger.error("Assignment not found")
        elif assignment_response.status_code == 403:
            response = service.prepare_response(403)
            logger.error("Access to assignment is Forbidden")
        else:
            response = service.prepare_response(503)
            logger.error(service.prepare_response(503))
            logger.error("Something went wrong :((")

        return response
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
    app.run(host='0.0.0.0', port=3001)
