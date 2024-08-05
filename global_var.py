import json
import os

import pandas as pd
topic_model_path = "/workspace/model/health_article_topic_model.bin"
SENTENCE_SPLIT = r"[。.!?！？]"
client_url = 'mongodb://10.48.48.7:27017/'
database_name = 'health_articles'
health_articles_folder_path = "/workspace/dataset/health/article"
def txt2list(folder_path: str):
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
                for line in file:
                    words_list.append(line.strip())
    return words_list

def get_stop_word()->list:
    with open('data/stop_words.txt', 'r') as file:
        stop_words = [word.strip() for word in file.readlines()]
    return stop_words


def get_field_map()->dict:
    with open("data/field_map.json", "r") as f:
        field_dict = json.load(f)
    return field_dict


def get_sentiment_dict()->dict:
    with open("data/sentiment_dict.json", "r") as file:
        sentiment_dict = json.load(file)
    return sentiment_dict

def get_medical_list()->list:
    medical_list = txt2list('chinese_medical_words')
    return medical_list


def get_real_pos()->dict:
    real_df = pd.read_csv('data/pos.csv')
    real_is_dict = dict(zip(real_df["en"], real_df["isreal"]))
    return real_is_dict

def get_word_dict():
    with open('data/word_dict.json', "r") as f:
        wordDictionary = json.load(f)
    return wordDictionary

def get_rare_list():
    with open('data/rare_words.txt', 'r', encoding='utf-8') as file:
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
