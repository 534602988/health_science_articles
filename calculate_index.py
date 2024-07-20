from collections import Counter
import json
import os
import re
import numpy as np
import pandas as pd
import torch
from process_mongo import get_db, insert_with_check
import jieba.posseg as pseg
from bs4 import BeautifulSoup
from collections import Counter

LONG2SHORT = 10
SENTENCE_SPLIT = r"[。.!?！？]"
DATABASE = get_db()
conjunctions_prepositions = [
    "和",
    "但",
    "或",
    "因为",
    "所以",
    "然而",
    "虽然",
    "如果",
    "但是",
    "因此",
    "于是",
    "即使",
    "可是",
    "并且",
    "还有",
    "是",
]
metaphorical_expressions = [
    "如",
    "像",
    "似",
    "仿佛",
    "宛如",
    "好像",
    "彷佛",
    "犹如",
    "有如",
    "仿若",
    "恰似",
    "犹若",
    "如同",
    "等于",
    "仿佛是",
    "彷佛是",
    "无异于",
    "胜似",
    "简直像",
    "堪比",
    "有如",
    "赛过",
    "好比",
    "如同是",
    "仿如",
]


def txt2list(folder_path: str):
    words_list = []
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否是 txt 文件
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    words_list.append(line.strip())
    return words_list


def sum_occurrences(a: list, b: list):
    counter_b = Counter(b)
    total_occurrences = sum(counter_b[element] for element in a)
    return total_occurrences


def count_html_elements(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    # 统计各类元素的数量
    img_count = len(soup.find_all("img"))
    audio_count = len(soup.find_all("audio"))
    video_count = len(soup.find_all("video"))
    p_count = len(soup.find_all("p"))
    table_count = len(soup.find_all("table"))
    link_count = len(soup.find_all("a"))
    return {
        "images": img_count,
        "audio": audio_count,
        "video": video_count,
        "paragraphs": p_count,
        "tables": table_count,
        "links": link_count,
    }


def count_about_word(words):
    word_counts = Counter(words)
    unique_words = [word for word, count in word_counts.items() if count == 1]
    unique_word_count = len(unique_words)
    total_word_count = len(words)
    word_ratio = word_counts / total_word_count if total_word_count > 0 else 0
    word_lengths = [len(word) for word in words]
    average_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
    return {
        "unique_word_count": unique_word_count,
        "word_ratio": word_ratio,
    }


def count_word_pos(text):
    words = pseg.cut(text)
    # 统计词性
    pos_counts = {}
    pos_list = []
    for word, flag in words:
        pos_list.append(flag)
        if flag not in pos_counts:
            pos_counts[flag] = 0
        pos_counts[flag] += 1
    return {"pos_count": pos_counts, "pos_list": pos_list}


def count_about_sentence(text: str, pos_list: list):
    sentences = re.split(SENTENCE_SPLIT, text)
    sentence_lengths = [len(sentence.strip()) for sentence in sentences]
    sentence_count = len(sentences)
    long_sentence_count = len(
        [sentence for sentence in sentences if len(sentence.strip()) > LONG2SHORT]
    )
    sentence_length_dev = float(np.std(sentence_lengths) if sentence_lengths else 0)
    short_sentence_count = sentence_count - long_sentence_count
    average_length = (
        sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    )
    cohesive = 1 / average_length
    mark_count = pos_list.count("x")
    v = pos_list.count("v")
    a = pos_list.count("a")
    return {
        "sentenced_length_dev": sentence_length_dev,
        "long_sentence_count": long_sentence_count,
        "short_sentence_count": short_sentence_count,
        "sentence_count": sentence_count,
        "average_length": average_length,
        "cohesive": cohesive,
        "mark_radio": mark_count / len(pos_list),
        "break": mark_count / sentence_count,
        "v_a": v / (v + a + 0.0001),
    }


def count_sentiment(sentiment: list):
    sentiment_score = int(np.array(sentiment).mean())
    unique_sentiments = set(sentiment)
    return {
        "sentiment_score": sentiment_score,
        "sentiment_": len(unique_sentiments),
    }


def get_structure_index(record: dict):
    if "html" in record.keys():
        result = count_html_elements(record["html"])
        result["title"] = record["title"]
        return result


def count_about_dict(word_list):
    with open("data/word_dict.json", "r") as f:
        word_dict = json.load(f)
    assert_list = word_dict["assertion"]
    cite_list = word_dict["cite"]
    level_list = word_dict["level"]
    concession_list = word_dict["concession"]
    turning_list = word_dict["turning"]
    medical_list = txt2list("chinese_medical_words")
    return {
        "assertion": sum_occurrences(word_list, assert_list),
        "cite": sum_occurrences(word_list, cite_list),
        "level": sum_occurrences(word_list, level_list),
        "concession": sum_occurrences(word_list, concession_list),
        "turning": sum_occurrences(word_list, turning_list),
        "medical": sum_occurrences(word_list, medical_list),
    }


def count_rare(text, rare_word):
    content_chars = list(rare_word)
    char_counts = {char: text.count(char) for char in content_chars}
    total_count = sum(char_counts.values())
    return {"rare": total_count}


def count_isreal(pos_count: dict, is_real: dict):
    real, unreal = 0, 0
    for key in pos_count.keys():
        if is_real[key] == 1:
            real += pos_count[key]
        else:
            unreal += pos_count[key]
    return {"real": real / (unreal + real)}


def count_parallelism(word_list):
    from collections import defaultdict
    filtered_lst = [item for item in word_list if item in conjunctions_prepositions]
    positions = defaultdict(list)
    for idx, value in enumerate(filtered_lst):
        positions[value].append(idx)
    result = []
    for value, pos_list in positions.items():
        if len(pos_list) >= 3:
            count = 0
            for i in range(len(pos_list) - 1):
                for j in range(i + 1, len(pos_list)):
                    if pos_list[j] - pos_list[i] < 5:
                        count += 1
                        if count >= 3:
                            result.append(value)
                            break
                if count >= 3:
                    break

    return {"parallelism": len(result)}


def count_metaphor(word_list):
    return {"metaphor": sum_occurrences(word_list, metaphorical_expressions)}

def count_fog(avg_sentence_len, complex_words_percentage):
    return {"fog": 0.8 * avg_sentence_len + complex_words_percentage}
    
# def get_pos(record:dict):
#     if 'text' in record.keys():
#         result = count_word_pos(record['text'])
#         result['title'] = record['title']
#         return result


def keyword_generation(model, tokenizer, text):
    # tokenize
    text = f"'关键词抽取':【{text}】这篇文章的关键词是什么？"
    encode_dict = tokenizer(text, max_length=512, padding="max_length", truncation=True)

    inputs = {
        "input_ids": torch.tensor([encode_dict["input_ids"]]).long(),
        "attention_mask": torch.tensor([encode_dict["attention_mask"]]).long(),
    }

    # generate answer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs["input_ids"] = inputs["input_ids"].to(device)
    inputs["attention_mask"] = inputs["attention_mask"].to(device)

    logits = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=100,
        do_sample=True,
        # early_stopping=True,
    )

    logits = logits[:, 1:]
    predict_label = [tokenizer.decode(i, skip_special_tokens=True) for i in logits]
    return {"predict_label": predict_label}


if __name__ == "__main__":
    records = DATABASE["articles"].find()
    for record in records:
        print(count_metaphor(record["text_seg"].split(" ")))
