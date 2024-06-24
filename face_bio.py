import ipdb
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from deepface import DeepFace

from typing import List

FACE_EMBEDDING_DIM = 512

executor = ThreadPoolExecutor(max_workers=4)

async def get_embeddings(path : str) -> List:
    """
    Get the embeddings of the audio file.

    Args:
        path (str): The path to the audio file.

    Returns:
        list: The embeddings of the
    """

    try:
        emb_objs = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(DeepFace.represent, path, model_name="Facenet512", detector_backend="retinaface", anti_spoofing=True)
        )

        emb = emb_objs[0]["embedding"]
    except Exception as e:
        print(e)
        return []

    return emb

async def is_same_face(emb_1 : List, emb_2 : List) -> bool:
    """
    Compare two face embeddings to determine if they belong to the same person.

    Args:
        emb_1 (List): The first face embedding.
        emb_2 (List): The second face embedding.
        threshold (float): The threshold for the similarity score.
    
    Returns:
        bool: True if the embeddings belong to the same person, False otherwise.
    """

    try:
        # verify = await asyncio.get_event_loop().run_in_executor(
        #     executor,
        #     DeepFace.verify,
        #     emb_1,
        #     emb_2,
        #     "Facenet512",
        #     "retinaface",
        #     threshold,
        #     True
        # )

        verify = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(DeepFace.verify, emb_1, emb_2, model_name="Facenet512", detector_backend="retinaface", anti_spoofing=True)
        )

    except Exception as e:
        print(e)
        return False

    return verify['verified']