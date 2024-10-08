from __future__ import annotations

import ipdb
from typing import Generator, List

from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.responses import JSONResponse

from sqlmodel import create_engine, Session

import shutil
import uuid
from pathlib import Path

import src.face_bio as face_bio
import src.voice_bio as voice_bio

from models.user import User, UserUpdate
from utils.errors import Error
from utils.annoy_index_manager import AnnoyIndexManager
from utils.response_manager import ResponseManager

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)

DATABASE_DIRECTORY = Path("db")
DATABASE_DIRECTORY.mkdir(exist_ok=True)

DATABASE_URL = "sqlite:///db/users.db"

index_face = AnnoyIndexManager("db/face_index.ann", face_bio.FACE_EMBEDDING_DIM)
index_voice = AnnoyIndexManager("db/voice_index.ann", voice_bio.VOICE_EMBEDDING_DIM)

app = FastAPI()

engine = create_engine(DATABASE_URL)
User.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Gets a new database session.

    Returns:
        Session: The database session.
    """

    with Session(engine) as session:
        yield session

def copy_temp_file(file: UploadFile, filename: str) -> Path:
    """
    Copies a temporary file to a new location.

    Parameters:
        file (UploadFile): The temporary file to copy.
        filename (str): The name of the new file.

    Returns:
        Path: The path to the new file.
    """

    path = UPLOAD_DIRECTORY / filename

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return path

@app.get("/")
def home() -> JSONResponse:
    """
    Returns the home page.

    Returns:
        JSONResponse: A JSON response containing the home page.
    """

    data = {
        "message": "Welcome to the Voice and Face Biometric Authentication API!"
    }

    return ResponseManager.success_response(data)

@app.post("/authorize")
async def authorize(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),

    session: Session = Depends(get_session)
) -> JSONResponse:
    """
    Logs in an existing user.

    Parameters:
        image (File): The user's face image.
        audio (File): The user's voice audio.

    Returns:
        JSONResponse: A JSON response indicating that the user has been logged in.
    """

    image_extension = image.filename.split(".")[-1]
    audio_extension = audio.filename.split(".")[-1]
    image_filename = f"{uuid.uuid4()}.{image_extension}"
    audio_filename = f"{uuid.uuid4()}.{audio_extension}"

    image_path = copy_temp_file(image, image_filename)
    audio_path = copy_temp_file(audio, audio_filename)

    pred_embs_voice = await voice_bio.get_embeddings(str(audio_path))
    pred_embs_face = await face_bio.get_embeddings(str(image_path))

    if not pred_embs_voice or not pred_embs_face:
        image_path.unlink()
        audio_path.unlink()

        return ResponseManager.get_error_response(Error.UNAUTHORIZED)

    pred_voice_ids, _ = index_voice.get_ids(pred_embs_voice)
    pred_face_ids, _ = index_face.get_ids(pred_embs_face)

    # The user exists and the IDs match
    if pred_voice_ids and pred_face_ids:
        pred_user_voice_embs = index_voice.get_vectors(pred_voice_ids[0])
        pred_user_face_embs = index_face.get_vectors(pred_face_ids[0])

        is_same_voice = await voice_bio.is_same_speaker(pred_embs_voice, pred_user_voice_embs)
        is_same_face = await face_bio.is_same_face(pred_embs_face, pred_user_face_embs)

        # Check if the voice and face embeddings match
        if (is_same_voice and is_same_face) and (pred_voice_ids[0] == pred_face_ids[0]):
            user = User.get_user(session, pred_voice_ids[0])

            data = {
                "user": user
            }

            image_path.unlink()
            audio_path.unlink()

            return ResponseManager.success_response(data)
        
        # The voice and face embeddings do not match, unauthorized access
        elif is_same_voice or is_same_face:
            image_path.unlink()
            audio_path.unlink()

            return ResponseManager.get_error_response(Error.UNAUTHORIZED)

        else:
            # The user does not exist, create a new user
            return create_user(session, pred_embs_voice, pred_embs_face, image_path, audio_path)

    else: # The user does not exist, create a new user
        return create_user(session, pred_embs_voice, pred_embs_face, image_path, audio_path)

@app.get("/db/users")
def get_all_users(session: Session = Depends(get_session)) -> JSONResponse:
    """
    Gets all users.

    Args:
        session (Session): The database session.

    Returns:
        JSONResponse: A JSON response containing all users.
    """

    users = User.get_all_users(session)

    data = {
        "users": users
    }

    return ResponseManager.success_response(data)

@app.get("/user/{userID}")
def get_user(userID: int, session: Session = Depends(get_session)) -> JSONResponse:
    """
    Gets all users.

    Args:
        userID (int): The ID of the user.
        session (Session): The database session.

    Returns:
        JSONResponse: A JSON response containing all users.
    """

    user = User.get_user(session, userID)

    if user:
        data = {
            "user": user
        }

        return ResponseManager.success_response(data)

    return ResponseManager.get_error_response(Error.USER_NOT_FOUND)

@app.patch("/user/{userID}")
def update_user(userID: int,
                update_data: UserUpdate,
                session: Session = Depends(get_session)) -> JSONResponse:
    """
    Updates a user.

    Args:
        userID (int): The ID of the user.
        update_data (Dict): The data to update.
        session (Session): The database session.

    Returns:
        JSONResponse: A JSON response indicating that the user has been updated.
    """

    user = User.update_user(session, userID, update_data)

    if user:
        data = {
            "user": user
        }

        return ResponseManager.success_response(data)
    
    return ResponseManager.get_error_response(Error.USER_NOT_FOUND)

@app.delete("/user/{userID}")
def delete_user(userID: int, session: Session = Depends(get_session)) -> JSONResponse:
    """
    Deletes a user.

    Args:
        userID (int): The ID of the user.
        session (Session): The database session.

    Returns:
        JSONResponse: A JSON response indicating that the user has been deleted.
    """

    all_ids = [user.id for user in User.get_all_users(session)]
    is_deleted = User.delete_user(session, userID) and index_voice.delete(userID, all_ids) and index_face.delete(userID, all_ids)

    if is_deleted:
        return ResponseManager.success_response()

    return ResponseManager.get_error_response(Error.USER_NOT_FOUND)

def create_user(session: Session,
                pred_embs_voice: List,
                pred_embs_face: List,
                image_path: Path,
                audio_path: Path) -> JSONResponse:
    """
    Creates a new user.

    Parameters:
        pred_embs_voice (List): The voice embeddings of the user.
        pred_embs_face (List): The face embeddings of the user.
        image_path (Path): The path to the user's face image.
        audio_path (Path): The path to the user's voice audio.
    
    Returns:
        JSONResponse: A JSON response indicating that the user has been created.
    """

    all_users = User.get_all_users(session)
    all_user_ids = [user.id for user in all_users]
    next_id = User.get_next_id(session)
    is_voice_added = index_voice.add(next_id, pred_embs_voice, all_user_ids)
    is_face_added = index_face.add(next_id, pred_embs_face, all_user_ids)

    if is_voice_added and is_face_added:
        new_user = User.add_user(session, next_id)

        image_path.unlink()
        audio_path.unlink()

        data = {
            "user": new_user
        }

        return ResponseManager.success_response(data)

    else:
        image_path.unlink()
        audio_path.unlink()

        return ResponseManager.get_error_response(Error.INTERNAL_SERVER_ERROR)