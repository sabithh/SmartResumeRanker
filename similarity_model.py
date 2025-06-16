from sentence_transformers import SentenceTransformer, util

# Load a pre-trained SBERT model. This happens only once.
# 'all-MiniLM-L6-v2' is a good, fast model.
model = SentenceTransformer('all-MiniLM-L6-v2')


def calculate_similarity(text1, text2):
    """
    Calculates the semantic similarity between two texts using SBERT.
    Returns a score between 0 and 1.
    """
    # Generate embeddings for both texts
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)

    # Compute cosine similarity
    cosine_scores = util.pytorch_cos_sim(embedding1, embedding2)

    # The result is a tensor, get the float value and scale to percentage
    score = cosine_scores.item() * 100

    return score