from __future__ import annotations

from ast import Tuple
import os
import ipdb

from annoy import AnnoyIndex

from typing import List, Tuple

NUM_TREES = 10

class AnnoyIndexManager:
    def __init__(self, index_path: str, vector_length: int, num_trees: int = NUM_TREES):
        """
        Initializes the AnnoyIndexManager.

        Args:
            index_path (str): The path to the index file.
            vector_length (int): The length of the vectors to be indexed.
            num_trees (int): The number of trees to build in the index.
        """

        self.index_path = index_path
        self.vector_length = vector_length
        self.num_trees = num_trees

        self.index = AnnoyIndex(self.vector_length, "angular")

        self.load_index()
    
    def add(self, id: int, vector: List[float], all_ids: List[int]) -> bool:
        """
        Adds a vector to the index.

        Args:
            id (int): The ID of the vector.
            vector (List[float]): The vector to be added to the index.
        """

        try:
            new_index = self.__copy__(all_ids)
            new_index.add_item(id, vector)

            self.rebuild_index(new_index)
            self.save_index()

            return True
        except Exception as e:
            print(f"Error adding vector to index: {e}")
            return False

    def get_ids(self, vector: List[float], num_results: int = 1) -> Tuple[List[int], List[float]]:
        """
        Gets the IDs of the nearest vectors to the given vector.

        Args:
            vector (List[float]): The vector to search for.
            num_results (int): The number of results to return.

        Returns:
            List[int]: The IDs of the nearest vectors.
        """

        ids, dists = self.index.get_nns_by_vector(vector, num_results, include_distances=True)

        return ids, dists

    def get_vectors(self, ids: int) -> List[float]:
        """
        Gets the vectors corresponding to the given IDs.

        Args:
            ids (List[int]): The IDs of the vectors to retrieve.

        Returns:
            List[List[float]]: The vectors corresponding to the given IDs.
        """

        try:
            vectors = self.index.get_item_vector(ids)
        except Exception as e:
            return []

        return vectors
    
    def load_index(self) -> None:
        """
        Loads the index from the index file.
        """

        if os.path.exists(self.index_path):
            self.index.load(self.index_path)
    
    def save_index(self) -> None:
        """
        Saves the index to the index file.
        """

        self.index.save(self.index_path)

    def rebuild_index(self, new_index : AnnoyIndex) -> None:
        """
        Rebuilds the index from scratch.
        """

        new_index.build(self.num_trees)
        self.index = new_index
    
    def __copy__(self, all_ids: List[int]) -> AnnoyIndexManager:
        """
        Creates a copy of the AnnoyIndexManager.

        Returns:
            AnnoyIndexManager: The copy of the AnnoyIndexManager.
        """

        new_index = AnnoyIndex(self.vector_length, "angular")

        for i in all_ids:
            emb = self.index.get_item_vector(i)
            new_index.add_item(i, emb)

        return new_index
    
    def __sizeof__(self) -> int:
        """
        Returns the size of the index.
        """

        return self.index.get_n_items()