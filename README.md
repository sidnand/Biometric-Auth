# FinTech MVP Backend API

## Endpoints

## POST /authorize

### Description

Logs in an existing user by verifying the provided face image and voice audio. If the user does not exist, a new user is created.

### Parameters

- `image` (File): The user's face image file.
- `audio` (File): The user's voice audio file.

### Request

- **Content-Type:** `multipart/form-data`
- **Body:**
  - `image`: The image file representing the user's face.
  - `audio`: The audio file representing the user's voice.

### Response

- **Status Code:** 200
- **Description:** The user has been successfully authorized.
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
- **Description:** The provided face image and voice audio do not match, indicating unauthorized access.
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
- **Description:** An internal server error occurred during processing.
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

### Example

```bash
POST /authorize
Content-Type: multipart/form-data
Body:
  image: <face_image.jpg>
  audio: <voice_audio.wav>
```

## Development

Python 3.12.3
