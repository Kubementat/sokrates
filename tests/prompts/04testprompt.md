Create a REST API in Python with two endpoints: GET /v1/users and POST /v1/users. The purpose of this API is to manage user data in a system where users need to be retrieved and created programmatically.

In real-world applications, such an API could be used in systems where user management is essential, like social media platforms or e-commerce sites.

The API should adhere to the following structure:
- The GET /v1/users endpoint should return a JSON object containing a list of users. Each user should have at least an id, name, and email.
- The POST /v1/users endpoint should accept a JSON body with user details (name and email) and create a new user in the system. The response should be the created user in JSON format, including an id.

Here are example inputs and outputs:
- Example GET response: `{"users": [{"id": 1, "name": "John Doe", "email": "john@example.com"}]}`
- Example POST request body: `{"name": "Jane Doe", "email": "jane@example.com"}`
- Example POST response: `{"id": 2, "name": "Jane Doe", "email": "jane@example.com"}`

Additionally, provide curl commands for interacting with the endpoints:
- GET: `curl http://localhost:5000/v1/users`
- POST: `curl -X POST -H "Content-Type: application/json" -d '{"name":"Jane Doe","email":"jane@example.com"}' http://localhost:5000/v1/users`

Consider the following edge cases and error handling:
- If the database is empty, the GET endpoint should return an empty list.
- If a user with the same email already exists, the POST endpoint should return a 409 Conflict status code.
- If invalid data is sent (e.g., missing name or email), return a 400 Bad Request status code.
- For server errors, return a 500 Internal Server Error status code.

Implement logging with timestamps and levels (INFO, ERROR). Use colors in the console output for different log levels to improve readability. For example:
- INFO messages should be green.
- WARNING messages should be yellow.
- ERROR messages should be red.

For the implementation, use the following external libraries if they simplify the task:
- FastAPI for the REST framework (preferred due to its modern features).
- Pydantic for data validation and settings management.
- Python-dotenv for managing environment variables (e.g., database connection strings).