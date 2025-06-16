import re
import nltk # <-- ADDED
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Tell NLTK where to find the data package
nltk.data.path.append('./nltk_data/') # <-- ADDED

def preprocess_text(text):
    """Cleans and preprocesses raw text."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return " ".join(filtered_tokens)