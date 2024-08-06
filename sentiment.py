from collections import defaultdict
import re
import jieba
import pandas as pd
import pymongo
from tqdm import tqdm
import global_var
from process_mongo import get_db


def get_label_data(sentiment_dict_path:str = "data/sentiment.xlsx")->dict:
    """
    Reads sentiment data from an Excel file and returns a dictionary of labeled data.

    Args:
        sentiment_dict_path (str): The path to the Excel file containing the sentiment data. 
        Defaults to "data/sentiment.xlsx".

    Returns:
        dict: A dictionary containing labeled data, where the keys are the sentiment categories
        ("joy", "surprise", "anger", "sadness", "fear", "disgust") and the values are
        dictionaries mapping words to sentiment scores.
    """
    # Read sentiment data from the Excel file
    sem_data = pd.read_excel(sentiment_dict_path)
    # Iterate over each row in the data
    for i in range(sem_data.shape[0]):
        score = 0

        # Convert sentiment values of 2 to -1
        if sem_data.iloc[i, 6] == 2:
            sem_data.iat[i, 6] = -1
        if sem_data.iloc[i, 9] == 2:
            sem_data.iat[i, 9] = -1

        # Calculate the score based on the sentiment values
        score += sem_data.iloc[i, 5] * sem_data.iloc[i, 6]
        sem_data.iat[i, -1] = score
    # Define a dictionary to store the labeled data
    match_dict = {
        "joy": ["PA", "PE"],
        "surprise": ["PC"],
        "anger": ["NA"],
        "sadness": ["NB", "NJ", "NH", "PF"],
        "fear": ["NI", "NC", "NG"],
        "disgust": ["ND", "NE", "NN", "NK", "NL"],
    }
    label_dict = {}
    # Iterate over each sentiment category
    keys = match_dict.keys()
    for k in keys:
        word_dict = {}
        # Iterate over each row in the data
        for i in range(sem_data.shape[0]):
            label = sem_data.iloc[i, 4]
            # Check if the label matches the sentiment category
            if label in match_dict[k]:
                word_dict[sem_data.iloc[i, 0]] = sem_data.iloc[i, -1]
        # Add the word dictionary to the label dictionary
        label_dict[k] = word_dict
    # Return the labeled data dictionary
    return label_dict


def calculate_sentiment_sentence(sentence:str, sentiment_dict:dict) -> int:
    """
    Calculate the sentiment score of a given sentence based on a sentiment dictionary.

    Args:
        sentence (str): The input sentence to calculate the sentiment score for.
        sentiment_dict (dict): A dictionary containing sentiment scores for different words.

    Returns:
        int: The total sentiment score of the sentence.

    """
    # 分词
    words = jieba.lcut(sentence)
    # 计算情感值
    sentiment_scores = defaultdict(int)
    for word in words:
        _apply_sentiment_word_scores(
            sentiment_dict, word, sentiment_scores
        )
    sentiment_score = dict(sentiment_scores)
    total_score = sum(sentiment_score.values())
    return int(total_score)


def _apply_sentiment_word_scores(sentiment_dict: dict, word: str, sentiment_scores: dict) -> None:
    """
    Applies sentiment word scores to the given sentiment scores dictionary.

    Args:
        sentiment_dict (dict): A dictionary containing sentiment word scores for different emotions.
        word (str): The word for which sentiment scores are to be applied.
        sentiment_scores (dict): A dictionary containing sentiment scores for different emotions.

    Returns:
        None
    """
    sentiment_scores["joy"] += sentiment_dict["joy"].get(word, 0)
    sentiment_scores["surprise"] += sentiment_dict["surprise"].get(word, 0)
    sentiment_scores["anger"] += sentiment_dict["anger"].get(word, 0)
    sentiment_scores["sadness"] += sentiment_dict["sadness"].get(word, 0)
    sentiment_scores["fear"] += sentiment_dict["fear"].get(word, 0)
    sentiment_scores["disgust"] += sentiment_dict["disgust"].get(word, 0)


def calculate_sentiment_text(text: str, sentiment_dict: dict) -> dict:
    """
    Calculate the sentiment score for each sentence in the given text using the provided sentiment dictionary.

    Args:
        text (str): The text to analyze for sentiment.
        sentiment_dict (dict): A dictionary containing sentiment scores for words.

    Returns:
        dict: A dictionary containing the sentiment scores for each sentence in the text.
            The sentiment scores are stored in a list under the key 'sentiment_list'.
    """
    sentences = re.split(global_var.SENTENCE_SPLIT, text)
    sentiment_list = []
    for sentence in sentences:
        sentiment_score = calculate_sentiment_sentence(sentence, sentiment_dict)
        sentiment_list.append(sentiment_score)
    return {"sentiment_list": sentiment_list}


def get_sentiment_list(sentiment_dict:dict,read_collection:pymongo.collection.Collection,wrote_collection:pymongo.collection.Collection)->None:
    """
    Retrieves the sentiment of articles from a given database and updates/inserts the sentiment scores.

    Args:
        database (pymongo.database.Database): The database containing the articles.

    Returns:
        dict: A dictionary containing the counts of updated and inserted records.
    """
    records = list(read_collection.find())
    bulk_updates = []
    for record in tqdm(records, desc='Processing records sentiment_list',total=len(records)):
        if "text" not in record.keys():
            tqdm.write(f'Text not found in record with title = {record.get("title")}')
        else:
            text = record["text"]
            new_record = calculate_sentiment_text(text, sentiment_dict)
            new_record.update({"title": record["title"]})
            bulk_updates.append(
                pymongo.UpdateOne(
                    {"title": new_record["title"]}, {"$set": new_record}, upsert=True
                )
            )

    if bulk_updates:
        wrote_collection.bulk_write(bulk_updates)
    return None


if __name__ == "__main__":

    sentiment_dict = global_var.get_sentiment_dict()
    get_sentiment_list(sentiment_dict,get_db(),'articles','indexs')
