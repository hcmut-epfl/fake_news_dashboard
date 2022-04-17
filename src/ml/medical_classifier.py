import pickle
import re

from pyvi import ViTokenizer

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F300-\U0001FAD6"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)
    
def preprocess(texts):
    texts = [i.lower() for i in texts]
    texts = [remove_emoji(i) for i in texts]

    texts = [re.sub('[^\w\d\s]', '', i) for i in texts]
    
    texts = [re.sub('\s+|\n', ' ', i) for i in texts]
    texts = [re.sub('^\s|\s$', '', i) for i in texts]

    texts = [ViTokenizer.tokenize(i) for i in texts]

    return texts

class MedicalClassifier:

    def __init__(self):
        model_path = 'resources/tfidf_svm_v1.pkl'
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model

    def predict(self, X):
        X = self.model.predict(X)
        return X