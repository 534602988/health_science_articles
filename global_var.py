'''
it is a file that contains global variables and functions that are used in multiple files.
Notes:
1. the mongo database is only available in our lan network, so the client_url is not accessible. And if you want to use the mongo database, you need to change the client_url to your own.
2. the health_articles_folder_path is the path to the folder containing the health articles. We offer some test articles in the default folder, you can change it to your own folder. 
3. the topic model is too large to upload to the github, so you need to train the topic model by yourself and choose a path to save the model.
'''


import json
import os
import pandas as pd


SENTENCE_SPLIT = r"[。.!?！？]"
LONG2SHORT = 10
topic_model_path = "/workspace/model/health_article_topic_model.bin"
client_url = "mongodb://10.48.48.7:27017/"
database_name = "health_articles"
health_articles_folder_path = "/workspace/dataset/health/article"


def txt2list(folder_path: str) -> list:
    """
    Convert text files in a folder to a list of words.

    Args:
        folder_path (str): The path to the folder containing the text files.

    Returns:
        list: A list of words extracted from the text files.
    """
    words_list = []
    for filename in os.listdir(folder_path):
        # Check if the file is a txt file
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                words_list.extend(line.strip() for line in file)
    return words_list


def get_stop_word() -> list:
    """
    Get stop words from a file.

    Returns:
        list: List of stop words.
    """

    with open("data/stop_words.txt", "r") as file:
        stop_words = [word.strip() for word in file.readlines()]
    return stop_words


def get_field_map() -> dict:
    """
    Get a dictionary mapping fields from a JSON file.

    Returns:
        dict: Dictionary mapping fields.
    """

    with open("data/field_map.json", "r") as f:
        field_dict = json.load(f)
    return field_dict


def get_sentiment_dict() -> dict:
    """
    Get a sentiment dictionary from a JSON file.

    Returns:
        dict: Sentiment dictionary.
    """
    with open("data/sentiment_dict.json", "r") as file:
        sentiment_dict = json.load(file)
    return sentiment_dict


def get_medical_list() -> list:
    """
    Get a list of medical words from a text file.

    Returns:
        list: List of medical words.
    """

    return txt2list("chinese_medical_words")


def get_real_pos() -> dict:
    """
    Reads a CSV file containing English words and their corresponding "isreal" values,
    and returns a dictionary mapping English words to their "isreal" values.

    Returns:
        dict: A dictionary mapping English words to their "isreal" values.
    """

    real_df = pd.read_csv("data/pos.csv")
    return dict(zip(real_df["en"], real_df["isreal"]))


def get_word_dict() -> dict:
    """
    Retrieves the word dictionary from the specified file.
    Returns:
        dict: The word dictionary loaded from the file.
    """

    with open("data/word_dict.json", "r") as f:
        wordDictionary = json.load(f)
    return wordDictionary


def get_rare_list() -> list:
    """
    Reads a file containing rare words and returns a list of those words.
    Returns:
        list: A list of rare words.
    """
    with open("data/rare_words.txt", "r", encoding="utf-8") as file:
        rare_word = file.read()
    return list(rare_word)


if __name__ == "__main__":
    print(type(get_stop_word()))
    print(type(get_field_map()))
    print(type(get_sentiment_dict()))
    print(type(get_medical_list()))
    print(type(get_real_pos()))
    print(type(get_word_dict()))
    print(type(get_rare_list()))
    print(get_rare_list())
