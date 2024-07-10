from collections import Counter
import re
import numpy as np
from process_mongo import get_db, insert_with_check
import jieba.posseg as pseg
from bs4 import BeautifulSoup

LONG2SHORT = 10
SENTENCE_SPLIT = r"[。.!?]"
DATABASE = get_db()


def count_html_elements(html_content):
    # 解析HTML内容
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
        'unique_word_count':unique_word_count,
        'word_ratio':word_ratio,
    }


def count_word_pos(text):
    # 使用jieba进行分词和词性标注
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
    v= pos_list.count("v")
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
        "v_a": v/v+a+0.0001,
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


# def get_pos(record:dict):
#     if 'text' in record.keys():
#         result = count_word_pos(record['text'])
#         result['title'] = record['title']
#         return result

if __name__ == "__main__":
    records = DATABASE["articles"].find()
    for record in records:
        print(record["text"])
        print(count_about_sentence(record["text"], record["pos_list"]))
        break
        # Rest of the code
