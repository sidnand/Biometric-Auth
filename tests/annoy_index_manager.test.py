import os
import sys

import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from annoy_index_manager import AnnoyIndexManager

class TestAnnoyIndexManager(unittest.TestCase):
    def setUp(self):
        self.index_path = 'test_index.ann'
        self.vector_length = 5
        self.num_trees = 10
        self.index_manager = AnnoyIndexManager(self.index_path, self.vector_length, self.num_trees)

    def tearDown(self):
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
    
    def test_sizeof(self):
        # Empty index
        size = self.index_manager.__sizeof__()
        
        self.assertEqual(size, 0)

        # Non-empty index
        id_1 = 0
        vector_1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        all_ids = []

        self.index_manager.add(id_1, vector_1, all_ids)

        size = self.index_manager.__sizeof__()

        self.assertEqual(size, 1)

    def test_add(self):
        # No IDs currently in the index
        id_1 = 0
        vector_1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        all_ids = []

        self.assertTrue(self.index_manager.add(id_1, vector_1, all_ids))

        # 1 ID currently in the index
        id_2 = 1
        vector_2 = [5.0, 4.0, 3.0, 2.0, 1.0]
        all_ids = [id_1]

        self.assertTrue(self.index_manager.add(id_2, vector_2, all_ids))

        # >= 2 IDs currently in the index
        id_3 = 2
        id_4 = 3

        vector_3 = [1.0, 2.0, 3.0, 4.0, 5.0]
        vector_4 = [5.0, 4.0, 3.0, 2.0, 1.0]
        all_ids = [id_1, id_2]

        self.assertTrue(self.index_manager.add(id_3, vector_3, all_ids))
        self.assertTrue(self.index_manager.add(id_4, vector_4, all_ids))
    
    def test_get_ids(self):
        # No IDs currently in the index
        vector_0 = [0.0, 0.0, 0.0, 0.0, 0.0]

        ids, _ = self.index_manager.get_ids(vector_0)

        self.assertEqual(ids, [])

        # ID exists
        id_1 = 0
        vector_1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        all_ids = []

        self.index_manager.add(id_1, vector_1, all_ids)

        ids, _ = self.index_manager.get_ids(vector_1)

        self.assertEqual(ids, [0])

        # ID does not exist, returns closest ID
        vector_2 = [5.0, 0.0, 2.0, 1.0, 1.0]
        
        ids, _ = self.index_manager.get_ids(vector_2)

        self.assertEqual(ids, [0])
    
    def test_get_vectors(self):
        # No IDs currently in the index
        id = 0

        vectors = self.index_manager.get_vectors(id)

        self.assertEqual(vectors, [])

        # ID exists
        id_1 = 0
        vector_1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        all_ids = []

        self.index_manager.add(id_1, vector_1, all_ids)

        vectors = self.index_manager.get_vectors(id_1)

        self.assertEqual(vectors, vector_1)

        # ID does not exist
        vectors = self.index_manager.get_vectors(1)

        self.assertEqual(vectors, [])

if __name__ == '__main__':
    unittest.main()