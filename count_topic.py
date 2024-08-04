import os
import pymongo
import pymongo.collection
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from tqdm import tqdm
import global_var 
import torch


def count_topic(articles: list[str], info_dict: dict) -> int:
    topics = []
    for article in articles:
        topics.append(info_dict[article])
    return len(set(topics))


def count_topic_all(read_collection:pymongo.collection.Collection,wrote_collection:pymongo.collection.Collection) -> None:
    stop_words = global_var.get_stop_word()
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    umap_model = UMAP(
        n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=42
    )
    hdbscan_model = HDBSCAN(
        min_cluster_size=150,
        metric="euclidean",
        cluster_selection_method="eom",
        prediction_data=True,
    )
    vectorizer_model = CountVectorizer(stop_words=stop_words, min_df=2, ngram_range=(1, 2))
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
    records = read_collection.find({}, {"_id": 0, "title": 1, "text": 1})
    articles = []
    title2articles = {}
    for record in records:
        paragraphs = record["text"].split("\n")
        paragraphs = [paragraph for paragraph in paragraphs if len(paragraph) >= 6]
        title2articles[record["title"]] = paragraphs
        articles.extend(paragraphs)
    if os.path.exists("topic_model.bin"):
        topic_model = BERTopic.load("topic_model.bin")
    else:
        info_dict = _extracted_from_count_topic_all_35(
            embedding_model, articles, topic_model
        )
    bulk_updates = []

    for title in tqdm(title2articles.keys(),desc='Processing records topic count', total=len(title2articles.keys())):
        articles = title2articles[title]
        new_record = {"title": title, "count_topic": count_topic(articles, info_dict)}
        # bulk_updates.append(
        #     pymongo.UpdateOne(
        #         {"title": new_record["title"]}, {"$set": new_record}, upsert=True
        #     )
        # )
        tqdm.write(str(new_record))
        wrote_collection.update_one({"title": new_record["title"]}, {"$set": new_record}, upsert=True)
    # if bulk_updates:
    #     wrote_collection.bulk_write(bulk_updates)
    return None


# TODO Rename this here and in `count_topic_all`
def _extracted_from_count_topic_all_35(embedding_model, articles, topic_model):
    print('start_embedding.....')
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("cuda is available to use")
    else:
        device = torch.device("cpu")
        print("cuda is unavailable")
    embeddings = embedding_model.encode(articles, show_progress_bar=True, device=device)
    print('start create topic .....')
    topic_model.fit_transform(articles, embeddings)
    topic_model.save("topic_model.bin")
    print("Topic model saved at topic_model.bin")
    info_df = topic_model.get_document_info(articles)
    return info_df[["Document", "Topic"]].set_index("Document")["Topic"].to_dict()

# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# umap_model = UMAP(
#     n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=42
# )
# hdbscan_model = HDBSCAN(
#     min_cluster_size=150,
#     metric="euclidean",
#     cluster_selection_method="eom",
#     prediction_data=True,
# )
# vectorizer_model = CountVectorizer(stop_words=stop_words, min_df=2, ngram_range=(1, 2))
# topic_model = BERTopic(
#     # Pipeline models
#     embedding_model=embedding_model,
#     umap_model=umap_model,
#     hdbscan_model=hdbscan_model,
#     vectorizer_model=vectorizer_model,
#     # Hyperparameters
#     top_n_words=10,
#     verbose=True,
# )
# database = get_db()
# records = database["articles"].find({}, {"_id": 0, "title": 1, "text": 1})
# articles = []
# title2articles = {}
# for record in records:
#     paragraphs = record["text"].split("\n")
#     paragraphs = [paragraph for paragraph in paragraphs if len(paragraph) >= 6]
#     title2articles.update({record["title"]: paragraphs})
#     articles.extend(paragraphs)
# embeddings = embedding_model.encode(articles, show_progress_bar=True)
# topic_model.fit_transform(articles, embeddings)
# info_df = topic_model.get_document_info(articles)
# info_dict = info_df[["Document", "Topic"]].set_index("Document")["Topic"].to_dict()
# bulk_updates = []
# for title in tqdm(title2articles.keys()):
#     articles = title2articles[title]
#     new_record = {"title": title, "count_topic": count_topic(articles, info_dict)}
#     bulk_updates.append(
#         pymongo.UpdateOne(
#             {"title": new_record["title"]}, {"$set": new_record}, upsert=True
#         )
#     )

# if bulk_updates:
#     database["indexs"].bulk_write(bulk_updates)
