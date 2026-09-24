import sys
import os
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# ADD PROJECT ROOT TO PATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from dataset.training_data import training_data

texts = [item[0] for item in training_data]
labels = [item[1] for item in training_data]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)

with open(os.path.join(BASE_DIR, "nlp_engine", "model.pkl"), "wb") as f:
    pickle.dump((vectorizer, model), f)

print(" ML Model trained and saved successfully")
