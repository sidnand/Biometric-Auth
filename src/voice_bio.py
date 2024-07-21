import os
import ipdb
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import torchvision
import torch

from speechbrain.inference.speaker import SpeakerRecognition

from typing import List, Tuple

VOICE_EMBEDDING_DIM = 192

in_dir = "uploads"

verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                                               savedir="pretrained_voice_models/spkrec-ecapa-voxceleb")

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
        waveform = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(verification.load_audio, path, savedir=in_dir)
        )
        batch = waveform.unsqueeze(0)

        emb = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(verification.encode_batch, batch, None, normalize=False)
        )

        emb = emb[0][0].tolist()
    except Exception as e:
        print(e)
        return []

    return emb

def list_to_tensor(emb : List) -> torch.Tensor:
    """
    Convert a list to a PyTorch tensor.

    Args:
        emb (List): The list to convert.

    Returns:
        torch.Tensor: The PyTorch tensor.
    """

    return torch.tensor(emb)

async def is_same_speaker(emb_1 : List, emb_2 : List, threshold : float = 0.30) -> Tuple[bool, float]:
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
        # Convert lists to tensors
        emb_1_tensor = list_to_tensor(emb_1)
        emb_2_tensor = list_to_tensor(emb_2)
        
        # Run the blocking similarity operation in a separate thread
        score = await asyncio.get_event_loop().run_in_executor(
            executor,
            partial(verification.similarity, emb_1_tensor, emb_2_tensor)
        )
        pred = score > threshold
    except Exception as e:
        print(e)
        return False, 0.0

    return pred.item()