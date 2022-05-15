from sentence_transformers import SentenceTransformer
import numpy as np

from feature.preprocessing.general import TextEmbedding

class BertProcessorDistDE:

    model = None

    def setup(self):
        if not self.__class__.model:
            #BertProcessor.model = SentenceTransformer("bert-base-german-cased")
            self.__class__.model = SentenceTransformer("/models/dbmdz/distilbert-base-german-europeana-cased")


    def process(self, text):
        #, show_progress_bar=False
        embedding = self.__class__.model.encode(text)
        embedding_half = embedding.astype(np.float16)
        return TextEmbedding(embedding_half)

    def clear(self):
        self.__class__.model = None

class BertProcessorBaseEN:

    model = None

    def setup(self):
        if not self.__class__.model:
            self.__class__.model = SentenceTransformer("/models/sentence-transformers/bert-base-nli-mean-tokens")


    def process(self, text):
        #, show_progress_bar=False
        embedding = self.__class__.model.encode(text)
        embedding_half = embedding.astype(np.float16)
        return TextEmbedding(embedding_half)

    def clear(self):
        self.__class__.model = None