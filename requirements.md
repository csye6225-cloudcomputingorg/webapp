# Assignment 1 - RESTful API

## RESTful API Requirements

- All API request/response payloads should be in JSON.
- No UI should be implemented for the application.
- As a user, I expect all API calls to return with a proper HTTP status code.
- As a user, I expect the code quality of the application to be maintained to the highest standards using the unit and/or integration tests.

## Health Check RESTful API

- The question we want to answer is How to detect that a running service instance is unable to handle requests?.
- The health check API is a way for us to monitor the health of the application instance and alerts us when something is not working as expected.
- Health check API allows us to stop sending traffic to unhealthy instances of the application and to automatically replace/repair them. It also helps us improve user experience by not routing their quests to unhealthy instances.

## A Health Check API may check for following:

- Database connection - Make sure the application is connected to the database or is able to establish connection at the time of the health check.
- Downstream API Calls - Your application may depend on other downstream APIs and outage of downstream API without which you cannot complete the users request.

## For this assignment, we are going to implement an endpoint /healthz that will do the following when called:

- Check if the application has connectivity to the database.
- Return HTTP 200 OK if the connection is successful.
- Return HTTP 503 Service Unavailable if the connection is unsuccessful.
- The API response should not be cached. Make sure to add cache-control: 'no-cache' header to the response.
- The API request should not allow for any payload.
- The API response should not include any payload.
- Only HTTP GET method is supported for the /healthz endpoint.

## Example Requests

### Success

curl -vvvv http://localhost:8080/healthz
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /healthz HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/8.1.2
> Accept: */*
>
< HTTP/1.1 200 OK
< Cache-Control: no-cache, no-store, must-revalidate;
< Pragma: no-cache
< X-Content-Type-Options: nosniff
< Date: Wed, 20 Sep 2023 01:18:37 GMT
< Content-Length: 0
<
* Connection #0 to host localhost left intact

### Failure

 $ curl -vvvv http://localhost:8080/healthz
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /healthz HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/8.1.2
> Accept: */*
>
< HTTP/1.1 503 Service Unavailable
< Cache-Control: no-cache, no-store, must-revalidate;
< Pragma: no-cache
< X-Content-Type-Options: nosniff
< Date: Wed, 20 Sep 2023 01:18:57 GMT
< Content-Length: 0
<
* Connection #0 to host localhost left intact

### 405 Method Not Allowed

 $ curl -vvvv -XPUT http://localhost:8080/healthz
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> PUT /healthz HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/8.1.2
> Accept: */*
>
< HTTP/1.1 405 Method Not Allowed
< Cache-Control: no-cache, no-store, must-revalidate;
< Pragma: no-cache
< X-Content-Type-Options: nosniff
< Date: Wed, 20 Sep 2023 01:38:11 GMT
< Content-Length: 0
<
* Connection #0 to host localhost left intact

## Submission

- Create a folder with the naming convention firstname_lastname_neuid_## where ## is the assignment number.
- Copy complete code for the assignment into this folder.
- Create a create a zip of the firstname_lastname_neuid_## directory. The zip file should be firstname_lastname_neuid_##.zip.
- Now unzip the zip file in some other directory and confirm the content of the zip files.
- Upload the Zip to the correct assignment in Canvas.
- You are allowed to resubmit. If you think there may be an issue with the ZIP file, feel free to submit it again. Only the latest submission will be graded.
