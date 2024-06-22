from __future__ import annotations

import ipdb
from typing import Generator

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.responses import JSONResponse

from sqlmodel import create_engine, Session

import shutil
import uuid
from pathlib import Path
from datetime import timedelta

import face_bio
import voice_bio

from models.user import User
from errors import Error
from annoy_index_manager import AnnoyIndexManager
from response_manager import ResponseManager

DATABASE_URL = "sqlite:///users.db"

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)

index_face = AnnoyIndexManager("face_index.ann", face_bio.FACE_EMBEDDING_DIM)
index_voice = AnnoyIndexManager("voice_index.ann", voice_bio.VOICE_EMBEDDING_DIM)

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

    pred_embs_voice = voice_bio.get_embeddings(str(audio_path))
    pred_embs_face = face_bio.get_embeddings(str(image_path))

    if not pred_embs_voice or not pred_embs_face:
        image_path.unlink()
        audio_path.unlink()

        return ResponseManager.get_error_response(Error.UNAUTHORIZED)

    pred_voice_ids, _ = index_voice.get_ids(pred_embs_voice)
    pred_face_ids, _ = index_face.get_ids(pred_embs_face)

    # The user exists and the IDs match
    if (pred_voice_ids and pred_face_ids) and (pred_voice_ids[0] == pred_face_ids[0]):
        pred_user_voice_embs = index_voice.get_vectors(pred_voice_ids[0])
        pred_user_face_embs = index_face.get_vectors(pred_face_ids[0])

        is_same_voice = voice_bio.is_same_speaker(pred_embs_voice, pred_user_voice_embs)
        is_same_face = face_bio.is_same_face(pred_embs_face, pred_user_face_embs)

        # Check if the voice and face embeddings match
        if is_same_voice and is_same_face:
            user = User.get_user(session, pred_voice_ids[0])

            data = {
                "user": user
            }

            image_path.unlink()
            audio_path.unlink()

            return ResponseManager.success_response(data)
        else: # The voice and face embeddings do not match, unauthorized access
            image_path.unlink()
            audio_path.unlink()

            return ResponseManager.get_error_response(Error.UNAUTHORIZED)

    else: # The user does not exist, create a new user
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
