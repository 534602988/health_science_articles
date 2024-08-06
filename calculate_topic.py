import collections
import os
import pymongo
import pymongo.collection
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from tqdm import tqdm
import global_var
import torch
from cuml.manifold import UMAP
from cuml.cluster import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from global_var import topic_model_path

# Prepare sub-models


def count_topic(articles: list[str], info_dict: dict) -> int:
    """
    Counts the number of unique topics in a list of articles.

    Args:
        articles (list[str]): A list of article names.
        info_dict (dict): A dictionary mapping article names to their corresponding topics.

    Returns:
        int: The number of unique topics in the given list of articles.
    """
    topics = [info_dict[article] for article in articles]
    return len(set(topics))


def count_topic_all(
    read_collection: pymongo.collection.Collection,
    wrote_collection: pymongo.collection.Collection,
) -> None:
    """
    Fit BERTopic without actually performing any clustering.

    Args:
        read_collection: Collection to read data from.
        wrote_collection: Collection to write data to.

    Returns:
        None
    """
    # Fit BERTopic without actually performing any clustering
    records = read_collection.find({}, {"_id": 0, "title": 1, "text": 1})
    articles = []
    title2articles = {}
    for record in records:
        paragraphs = record["text"].split("\n")
        paragraphs = [paragraph for paragraph in paragraphs if len(paragraph) >= 6]
        title2articles[record["title"]] = paragraphs
        articles.extend(paragraphs)
    if os.path.exists(topic_model_path):
        topic_model = BERTopic.load("topic_model.bin")
        print("Topic model saved at topic_model.bin")
    else:
        topic_model = model_fit_save(articles, topic_model_path)
    bulk_updates = []
    info_df = topic_model.get_document_info(articles)
    info_dict = info_df[["Document", "Topic"]].set_index("Document")["Topic"].to_dict()
    for title in tqdm(
        title2articles.keys(),
        desc="Processing records topic count",
        total=len(title2articles.keys()),
    ):
        articles = title2articles[title]
        new_record = {"title": title, "count_topic": count_topic(articles, info_dict)}
        wrote_collection.update_one(
            {"title": new_record["title"]}, {"$set": new_record}, upsert=True
        )
    return None


def model_fit_save(articles: list, model_path: str) -> BERTopic:
    """
    Fits a BERTopic model to a list of articles and saves the model to a specified path.
    Args:
        articles (list): A list of articles.
        model_path (str): The path to save the BERTopic model.
    Returns:
        BERTopic: The fitted BERTopic model.
    Raises:
        None
    """
    # Extract vocab to be used in BERTopic
    vocab = collections.Counter()
    tokenizer = CountVectorizer().build_tokenizer()
    for doc in tqdm(articles):
        vocab.update(tokenizer(doc))
    vocab = [word for word, frequency in vocab.items() if frequency >= 15]
    len(vocab)
    stop_words = global_var.get_stop_word()
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    umap_model = UMAP(
        n_components=5, n_neighbors=50, random_state=42, metric="cosine", verbose=True
    )
    hdbscan_model = HDBSCAN(
        min_samples=20,
        gen_min_span_tree=True,
        prediction_data=False,
        min_cluster_size=20,
        verbose=True,
    )
    vectorizer_model = CountVectorizer(vocabulary=vocab, stop_words=stop_words)
    topic_model = BERTopic(
        # Pipeline models
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        # Hyperparameters
        top_n_words=10,
        verbose=True,
    )
    print("start_embedding.....")
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("cuda is available to use")
    else:
        device = torch.device("cpu")
        print("cuda is unavailable")
    embeddings = embedding_model.encode(articles, show_progress_bar=True, device=device)
    print("start create topic .....")
    topic_model.fit_transform(articles, embeddings)
    topic_model.save(model_path)
    return topic_model


if __name__ == "__main__":
    # Connect to MongoDB
    client = pymongo.MongoClient(global_var.client_url)
    database = client[global_var.database_name]
    articles = database["articles"]
    indexs = database["indexs_backend"]
    # indexs.insert_one({'title':'test'})
    print("starting write topic count")
    count_topic_all(articles, indexs)
    print("topic are successfully wrote")
