from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
import numpy as np
from sentence_transformers import SentenceTransformer


def tfidf_similarity(job_desc, resumes):
    # Combine job description + resumes
    documents = [job_desc] + resumes
   
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
   
    # Convert text into vectors
    tfidf_matrix = vectorizer.fit_transform(documents)
   
    # Compute similarity
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
   
    return similarity_scores[0]



def to_percentage(scores):
    return [round(score * 100, 2) for score in scores]


def tokenize(text):
    return text.split()


def train_word2vec(texts):
    tokenized_texts = [tokenize(text) for text in texts]
   
    model = Word2Vec(
        sentences=tokenized_texts,
        vector_size=100,
        window=5,
        min_count=1,
        workers=4
    )
   
    return model



def get_text_vector(model, text):
    words = tokenize(text)
    vectors = []
   
    for word in words:
        if word in model.wv:
            vectors.append(model.wv[word])
   
    if len(vectors) == 0:
        return np.zeros(model.vector_size)
   
    return np.mean(vectors, axis=0)



def word2vec_similarity(job_desc, resumes):
    documents = [job_desc] + resumes
   
    # Train model
    model = train_word2vec(documents)
   
    # Get vectors
    job_vector = get_text_vector(model, job_desc)
   
    scores = []
   
    for resume in resumes:
        resume_vector = get_text_vector(model, resume)
       
        similarity = cosine_similarity(
            [job_vector],
            [resume_vector]
        )[0][0]
       
        scores.append(similarity)
   
    return scores



def load_bert_model():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model


def bert_similarity(job_desc, resumes):
    model = load_bert_model()
   
    # Encode texts into vectors
    job_embedding = model.encode(job_desc)
    resume_embeddings = model.encode(resumes)
   
    scores = []
   
    for resume_vector in resume_embeddings:
       
        similarity = cosine_similarity(
            [job_embedding],
            [resume_vector]
        )[0][0]
       
        scores.append(similarity)
   
    return scores



def compare_models(job_desc, resumes, resume_names):
   
    #Model 1: TF-IDF 
    tfidf_scores = tfidf_similarity(job_desc, resumes)
   
    #Model 2: Word2Vec 
    w2v_scores = word2vec_similarity(job_desc, resumes)
   
    #Model 3: BERT
    bert_scores = bert_similarity(job_desc, resumes)
   
    results = []
   
    for i in range(len(resumes)):
       
        tfidf = tfidf_scores[i]
        w2v = w2v_scores[i]
        bert = bert_scores[i]
       
        # Final score (average)
        final_score = (tfidf + w2v + bert) / 3
       
        results.append({
            "resume_id": resume_names[i],
            "tfidf": round(tfidf * 100, 2),
            "word2vec": round(w2v * 100, 2),
            "bert": round(bert * 100, 2),
            "final": round(final_score * 100, 2)
        })
   
    return results



def rank_resumes(results):
   
    # Sort by final score (descending)
    sorted_results = sorted(
        results,
        key=lambda x: x["final"],
        reverse=True
    )
   
    return sorted_results


def get_top_resumes(sorted_results, top_n=5):
    return sorted_results[:top_n]

