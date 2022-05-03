
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from feature.preprocessing.general import TextEmbedding

class TfidfProcessor:

    def setup(self):
        pass


    def process(self, texts):
        #vectorizer = TfidfVectorizer(stop_words=None, tokenizer=lambda e: e, lowercase=False, max_features=10, max_df=0.8)
        vectorizer = TfidfVectorizer()
        embeddings_array = vectorizer.fit_transform(texts)
        #vectorizer.get_feature_names_out()

        return TextEmbedding(embeddings_array)

        