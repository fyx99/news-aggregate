# from unittest import mock
# import numpy as np
# from feature.preprocessing.general import SimilarityMatrix


# from test import CustomTestcase



# class TestSimilarity(CustomTestcase):

#     def test_similarity_matrix(self):
        
#         test_array = np.array([[1, 0.4, 0.5],[0.4, 1, 0.3],[0.5, 0.2, 1]])
#         similarityMatrix = SimilarityMatrix(test_array)
#         self.assertEqual(similarityMatrix.similarities[0,0], 0)
#         similarityOutput = similarityMatrix.top_n(1)
#         self.assertEqual(similarityOutput.indices[0, 0], 2)
#         self.assertEqual(similarityOutput.indices[1, 0], 0)
#         self.assertEqual(similarityOutput.indices[2, 0], 0)

        
#         similarityOutput = similarityMatrix.top_n(2)
#         self.assertEqual(similarityOutput.scores[0, 1], 0.5)
#         self.assertEqual(similarityOutput.scores[1, 1], 0.4)
#         self.assertEqual(similarityOutput.scores[2, 1], 0.5)



# if __name__ =="__main__":
#     TestSimilarity().test_similarity_matrix()