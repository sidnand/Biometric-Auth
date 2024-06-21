import os
import ipdb

import torchvision

from speechbrain.inference.speaker import SpeakerRecognition

from typing import List, Tuple

VOICE_EMBEDDING_DIM = 192

in_dir = "uploads"

verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                                               savedir="pretrained_voice_models/spkrec-ecapa-voxceleb")

def get_embeddings(path : str) -> List:
    """
    Get the embeddings of the audio file.

    Args:
        path (str): The path to the audio file.

    Returns:
        list: The embeddings of the
    """

    waveform = verification.load_audio(path, savedir=in_dir)
    batch = waveform.unsqueeze(0)
    emb = verification.encode_batch(batch, None, normalize=False)

    emb = emb[0][0].tolist()

    return emb

def is_same_speaker(emb_1 : List, emb_2 : List, threshold : float = 0.25) -> Tuple[bool, float]:
    """
    Compare two face embeddings to determine if they belong to the same person.

    Args:
        emb_1 (List): The first face embedding.
        emb_2 (List): The second face embedding.
        threshold (float): The threshold for the similarity score.

    Returns:
        bool: True if the embeddings belong to the same person, False otherwise.
    """
    
    score = verification.similarity(emb_1, emb_2)
    pred = score > threshold

    return pred, score