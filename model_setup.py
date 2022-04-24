from sentence_transformers import SentenceTransformer

def setup(model):
    modelPath = "/models/" + model

    model = SentenceTransformer('bert-base-nli-stsb-mean-tokens')
    model.save(modelPath)
    model = SentenceTransformer(modelPath)


if __name__ == "__main__":
    setup("sentence-transformers/bert-base-nli-mean-tokens")
    setup("dbmdz/distilbert-base-german-europeana-cased")