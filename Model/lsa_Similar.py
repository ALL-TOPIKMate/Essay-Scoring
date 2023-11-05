import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from PyKomoran import * #형태소 분석기 변경

tfidf_vectorizer = TfidfVectorizer()
komoran = Komoran('STABLE')

def preprocess_text(text):
    tokens = (komoran.get_plain_text(text)).split(' ')
    words = [token.split('/')[0] for token in tokens]
    return ' '.join(words)

def lsa_Similar(contents, answer):
    contents_preprocessed = preprocess_text(contents[0])
    answer_preprocessed = preprocess_text(answer[0])
    
    tfidf_matrix = tfidf_vectorizer.fit_transform([contents_preprocessed, answer_preprocessed])

    lsa = TruncatedSVD(n_components=2)
    lsa_matrix = lsa.fit_transform(tfidf_matrix)

    similarity_matrix = cosine_similarity(lsa_matrix)

    response = {
        'best_i': 0,
        'best_dist': 1 - similarity_matrix[1][0],
        'result': contents
    }

    return response