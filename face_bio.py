import ipdb

from deepface import DeepFace

from typing import List

FACE_EMBEDDING_DIM = 512

def get_embeddings(path : str) -> List:
    """
    Get the embeddings of the audio file.

    Args:
        path (str): The path to the audio file.

    Returns:
        list: The embeddings of the
    """

    try:
        emb_objs = DeepFace.represent(
            img_path = path,
            model_name = "Facenet512",
            detector_backend = "retinaface",
            anti_spoofing=True
        )

        emb = emb_objs[0]["embedding"]
    except Exception as e:
        print(f"Error getting embeddings: {str(e)}")
        return None

    return emb

def is_same_face(emb_1 : List, emb_2 : List, threshold : float = 0.25) -> bool:
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
        verify = DeepFace.verify(
            img1_path = emb_1,
            img2_path = emb_2,
            model_name = "Facenet512",
            detector_backend = "retinaface",
            threshold = threshold,
            anti_spoofing = True,
        )
    except Exception as e:
        print(f"Error verifying embeddings: {str(e)}")
        return False

    return verify['verified']