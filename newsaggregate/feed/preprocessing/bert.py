from sentence_transformers import SentenceTransformer
import numpy as np

from newsaggregate.feed.preprocessing.general import TextEmbedding

class BertProcessorDistDE:

    model = None

    def setup(self):
        if not self.__class__.model:
            #BertProcessor.model = SentenceTransformer("bert-base-german-cased")
            self.__class__.model = SentenceTransformer("/models/dbmdz/distilbert-base-german-europeana-cased")


    def process(self, text):
        #, show_progress_bar=False
        embedding = self.__class__.model.encode(text)
        embedding_array = np.array(embedding)
        return TextEmbedding(embedding_array)


class BertProcessorBaseEN:

    model = None

    def setup(self):
        if not self.__class__.model:
            self.__class__.model = SentenceTransformer("/models/sentence-transformers/bert-base-nli-mean-tokens")


    def process(self, text):
        #, show_progress_bar=False
        embedding = self.__class__.model.encode(text)
        embedding_array = np.array(embedding)
        return TextEmbedding(embedding_array)


