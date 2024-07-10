import codecs
from collections import defaultdict
import json
import re
import jieba
import pandas as pd
from process_mongo import get_db, insert_with_check
from calculate_index import SENTENCE_SPLIT


def get_label_data():
    SENTEIMENT_DICT_PATH = "data/sentiment.xlsx"
    sem_data = pd.read_excel(SENTEIMENT_DICT_PATH)
    for i in range(sem_data.shape[0]):
        score = 0
        if sem_data.iloc[i, 6] == 2:
            sem_data.iat[i, 6] = -1
        if sem_data.iloc[i, 9] == 2:
            sem_data.iat[i, 9] = -1
        # 是否需要辅助情感分类，目前先不要啦
        #     if sem_data.iloc[i,8] >= 0:
        #         score += sem_data.iloc[i, 8] * sem_data.iloc[i, 9]
        #         print(score)
        # 增加每个词语的情感强度值
        score += sem_data.iloc[i, 5] * sem_data.iloc[i, 6]
        sem_data.iat[i, -1] = score
    # 定义情感字典
    match_dict = {
        "joy": ["PA", "PE"],
        "surprise": ["PC"],
        "anger": ["NA"],
        "sadness": ["NB", "NJ", "NH", "PF"],
        "fear": ["NI", "NC", "NG"],
        "disgust": ["ND", "NE", "NN", "NK", "NL"],
    }
    # 获取情感类别
    label_dict = {}
    keys = match_dict.keys()
    for k in keys:
        word_dict = {}
        for i in range(sem_data.shape[0]):
            label = sem_data.iloc[i, 4]
            if label in match_dict[k]:
                word_dict[sem_data.iloc[i, 0]] = sem_data.iloc[i, -1]
        label_dict[k] = word_dict
    return label_dict


def calculate_sentiment_sentence(sentence, sentiment_dict):
    # 分词
    words = jieba.lcut(sentence)
    # 计算情感值
    sentiment_scores = defaultdict(int)
    for word in words:
        sentiment_scores["joy"] += sentiment_dict["joy"].get(word, 0)
        sentiment_scores["surprise"] += sentiment_dict["surprise"].get(word, 0)
        sentiment_scores["anger"] += sentiment_dict["anger"].get(word, 0)
        sentiment_scores["sadness"] += sentiment_dict["sadness"].get(word, 0)
        sentiment_scores["fear"] += sentiment_dict["fear"].get(word, 0)
        sentiment_scores["disgust"] += sentiment_dict["disgust"].get(word, 0)
    sentiment_score = dict(sentiment_scores)
    total_score = sum(sentiment_score.values())
    return int(total_score)


def calculate_sentiment_text(text, sentiment_dict):
    sentences = re.split(SENTENCE_SPLIT, text)
    sentiment_list = []
    for sentence in sentences:
        sentiment_score = calculate_sentiment_sentence(sentence, sentiment_dict)
        sentiment_list.append(sentiment_score)
    return {"sentiment_list": sentiment_list}


def get_sentiment():
    records = get_db()["articles"].find({"text": {"$ne": ""}}, {"text": 1, "title": 1})
    with open("data/sentiment_dict.json", "r") as file:
        sentiment_dict = json.load(file)
    updated_count = 0
    inserted_count = 0
    for record in records:
        text = record["text"]
        sentiment_score = calculate_sentiment_text(text, sentiment_dict)
        sentiment_score.update({"title": record["title"]})
        if insert_with_check(collection=get_db()["articles"], record=sentiment_score):
            inserted_count += 1
        else:
            updated_count += 1
    return {"updated_count": updated_count, "inserted_count": inserted_count}


if __name__ == "__main__":
    get_sentiment()
