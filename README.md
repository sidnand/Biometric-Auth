# FinTech MVP Backend API

## Endpoints

## GET /

Returns a welcome message.

## POST /authorize

Logs in an existing user by verifying the provided face image and voice audio. If the user does not exist, a new user is created.

- **Content-Type:** `multipart/form-data`
- **Body:**
  - `image`: The image file representing the user's face.
  - `audio`: The audio file representing the user's voice.

### Response

- **Status Code:** 200
- **Body:**
  
    ```json
    {
        "success": True,
        "data": {
            "user": {
            "id": <int>,
            "firstname": <null | str>,
            "lastname": <null | str>
            }
        }
    }
    ```

- **Status Code:** 401
- **Body:**
  
    ```json
    {
        "success": False,
        "error": {
            "code": "UNAUTHORIZED",
            "message": "Unauthorized access."
        }
    }
    ```

- **Status Code:** 500
- **Body:**
  
    ```json
    {
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred."
        }
    }
    ```

## GET /user/{userID}

Retrieves the user's information.

- **Content-Type:** `application/json`
- **Body:**
  - `userID`: The user's ID.

### Response

- **Status Code:** 200
- **Body:**
  
    ```json
    {
        "success": True,
        "data": {
            "user": {
            "id": <int>,
            "firstname": <null | str>,
            "lastname": <null | str>
            }
        }
    }
    ```

- **Status Code:** 404

## PATCH /user/{userID}

Updates the user's information.

- **Content-Type:** `application/json`
- **Body:**
  - `firstname`: The user's first name.
  - `lastname`: The user's last name.

### Response

- **Status Code:** 200
- **Body:**
  
    ```json
    {
        "success": True,
        "data": {
            "user": {
            "id": <int>,
            "firstname": <str>,
            "lastname": <str>
            }
        }
    }
    ```

- **Status Code:** 404

## DELETE /user/{userID}

Deletes the user's information.

- `userID` (int): The user's ID.
- **Content-Type:** `application/json`

### Response

- **Status Code:** 200
- **Body:**
  
    ```json
    {
        "success": True,
        "data": null
    }
    ```

## GET /db/users

Retrieves all users' information.

- **Content-Type:** `application/json`

### Response

- **Status Code:** 200
- **Body:**
  
    ```json
    {
        "success": True,
        "data": {
            "users": [
                { ... }
            ]
        }
    }
    ```

## Development

Python 3.12.3

Run with `uvicorn main:app --host 0.0.0.0 --port 8000`