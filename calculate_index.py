import math
import re
import traceback
import numpy as np
import pymongo
from tqdm import tqdm
import global_var
import jieba
import jieba.posseg as pseg
from bs4 import BeautifulSoup
from collections import Counter
from global_var import SENTENCE_SPLIT, LONG2SHORT
from pymongo.collection import Collection as PymongoCollection
from collections import Counter



def calculate_entropy(probabilities: dict) -> float:
    """
    Calculate the entropy of a probability distribution.

    Parameters:
    probabilities (dict): A dictionary containing the probabilities of each event.

    Returns:
    float: The entropy of the probability distribution.

    """
    return -sum(p * math.log2(p) for p in probabilities.values())


def sum_occurrences(a: list, b: list) -> int:
    """
    Calculates the total number of occurrences of elements in list 'a' in list 'b'.

    Args:
        a (list): The list of elements to count occurrences for.
        b (list): The list to search for occurrences in.

    Returns:
        int: The total number of occurrences of elements in list 'a' in list 'b'.
    """
    counter_b = Counter(b)
    return sum(counter_b[element] for element in a)


def count_html_elements(html_content: str) -> dict:
    """
    Counts the number of different HTML elements in the given HTML content.

    Args:
        html_content (str): The HTML content to be analyzed.

    Returns:
        dict: A dictionary containing the counts of various HTML elements.
            The keys represent the element types, and the values represent the counts.

    Example:
        >>> html_content = "<html><body><p>Hello, world!</p></body></html>"
        >>> count_html_elements(html_content)
        {'images': 0, 'audio': 0, 'video': 0, 'paragraphs': 1, 'tables': 0, 'links': 0}
    """
    soup = BeautifulSoup(html_content, "html.parser")
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


def count_about_word(words: list[str]) -> dict:
    """
    Counts various metrics related to a list of words.

    Args:
        words (list[str]): A list of words.

    Returns:
        dict: A dictionary containing the following metrics:
            - total_word_count: The total count of words.
            - unique_word_count: The count of unique words.
            - unique_word_percentage: The percentage of unique words.
            - non_repeating_word_count: The count of non-repeating words.
            - word_ratio: The ratio of non-repeating words to total words.
            - average_word_length: The average length of words.
            - entropy: The entropy calculated based on word probabilities.
    """
    # Count the occurrences of each word
    word_counts = Counter(words)
    # Count the number of unique words
    unique_word_count = len([word for word, count in word_counts.items() if count == 1])
    # Calculate the total count of words
    total_word_count = sum(word_counts.values())
    # Calculate the count of non-repeating words
    non_repeating_word_count = len(word_counts.items())
    # Calculate the probabilities of each word
    word_probabilities = {
        word: count / total_word_count for word, count in word_counts.items()
    }
    # Calculate the entropy based on word probabilities
    entropy = calculate_entropy(word_probabilities)
    # Calculate the ratio of non-repeating words to total words
    word_ratio = (
        non_repeating_word_count / total_word_count if total_word_count > 0 else 0
    )
    # Calculate the average length of words
    average_word_length = len("".join(words)) / total_word_count
    return {
        "total_word_count": total_word_count,
        "unique_word_count": unique_word_count,
        "unique_word_percentage": unique_word_count / total_word_count,
        "non_repeating_word_count": non_repeating_word_count,
        "word_ratio": word_ratio,
        "average_word_length": average_word_length,
        "entropy": entropy,
    }


def count_word_pos(text: str):
    """
    Count the occurrences of each part-of-speech tag in the given text.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing two keys:
            - 'pos_count': A dictionary mapping each part-of-speech tag to its count.
            - 'pos_list': A list of all part-of-speech tags in the order they appear in the text.
    """
    words = pseg.cut(text)
    pos_counts = {}
    pos_list = []
    for word, flag in words:
        pos_list.append(flag)
        if flag not in pos_counts:
            pos_counts[flag] = 0
        pos_counts[flag] += 1
    return {"pos_count": pos_counts, "pos_list": pos_list}


def count_about_sentence(text: str, pos_list: list) -> dict:
    """
    Counts various metrics related to sentences in a given text.

    Args:
        text (str): The input text.
        pos_list (list): A list of part-of-speech tags for each word in the text.

    Returns:
        dict: A dictionary containing the following metrics:
            - sentenced_length_dev (float): The standard deviation of sentence lengths.
            - long_sentence_count (int): The number of sentences that are longer than a threshold.
            - short_sentence_count (int): The number of sentences that are shorter than or equal to the threshold.
            - sentence_count (int): The total number of sentences.
            - average_sentence_length (float): The average length of sentences.
            - cohesive (float): A measure of sentence cohesion.
            - mark_radio (float): The ratio of "x" marks in the part-of-speech list.
            - break (float): The ratio of "x" marks per sentence.
            - v_a (float): The ratio of "v" marks to the sum of "v" and "a" marks.
    """
    # Split the text into sentences
    sentences = re.split(SENTENCE_SPLIT, text)
    # Calculate the length of each sentence
    sentence_lengths = [len(sentence.strip()) for sentence in sentences]
    # Count the total number of sentences
    sentence_count = len(sentences)
    # Count the number of sentences that are longer than a threshold
    long_sentence_count = len(
        [sentence for sentence in sentences if len(sentence.strip()) > LONG2SHORT]
    )
    # Calculate the standard deviation of sentence lengths
    sentence_length_dev = float(np.std(sentence_lengths) if sentence_lengths else 0)
    # Calculate the number of sentences that are shorter than or equal to the threshold
    short_sentence_count = sentence_count - long_sentence_count
    # Calculate the average length of sentences
    average_length = (
        sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    )
    # Calculate a measure of sentence cohesion
    cohesive = 1 / average_length
    # Count the number of "x" marks in the part-of-speech list
    mark_count = pos_list.count("x")
    # Count the number of "v" marks in the part-of-speech list
    v = pos_list.count("v")
    # Count the number of "a" marks in the part-of-speech list
    a = pos_list.count("a")
    return {
        "sentenced_length_dev": sentence_length_dev,
        "long_sentence_count": long_sentence_count,
        "short_sentence_count": short_sentence_count,
        "sentence_count": sentence_count,
        "average_sentence_length": average_length,
        "cohesive": cohesive,
        "mark_radio": mark_count / len(pos_list),
        "break": mark_count / sentence_count,
        "v_a": v / (v + a + 0.0001),
    }


def count_sentiment(sentiment_list: list) -> dict:
    """
    Calculates the sentiment score and sentiment variety based on the given list of sentiments.

    Args:
        sentiment_list (list): A list of sentiment values.

    Returns:
        dict: A dictionary containing the sentiment score and sentiment variety.

    Example:
        >>> count_sentiment([1, 2, 3, 4, 5])
        {'sentiment_score': 3, 'sentiment_variety': 5}
    """
    sentiment_score = int(np.array(sentiment_list).mean())
    unique_sentiments = set(sentiment_list)
    return {
        "sentiment_score": sentiment_score,
        "sentiment_variety": len(unique_sentiments),
    }


def count_about_structure(word_list: list, word_dict: dict) -> dict:
    """
    Counts the occurrences of words in a given word list based on the provided word dictionary.

    Args:
        word_list (list): A list of words to count occurrences for.
        word_dict (dict): A dictionary containing word categories as keys and corresponding word lists as values.

    Returns:
        dict: A dictionary containing the counts of occurrences for each word category in the word dictionary.
    """
    assert_list = word_dict["assertion"]
    cite_list = word_dict["cite"]
    level_list = word_dict["level"]
    concession_list = word_dict["concession"]
    turning_list = word_dict["turning"]
    return {
        "assertion": sum_occurrences(word_list, assert_list),
        "cite": sum_occurrences(word_list, cite_list),
        "level": sum_occurrences(word_list, level_list),
        "concession": sum_occurrences(word_list, concession_list),
        "turning": sum_occurrences(word_list, turning_list),
    }


def count_medical(word_list: list, medical_list: list) -> dict:
    """
    Counts the occurrences of medical words in a given word list.

    Args:
        word_list (list): The list of words to search for medical terms.
        medical_list (list): The list of medical terms to count.

    Returns:
        dict: A dictionary containing the count of medical terms found in the word list.
    """
    return {
        "medical": sum_occurrences(word_list, medical_list),
    }


def count_rare(text: str, rare_word: list) -> dict:
    """
    Counts the occurrences of rare words in a given text and calculates the percentage.

    Args:
        text (str): The text to search for rare words.
        rare_word (list): A list of rare words to count.

    Returns:
        dict: A dictionary containing the total count of rare words and the percentage of rare words in the text.
    """
    content_chars = list(rare_word)
    char_counts = {char: text.count(char) for char in content_chars}
    total_count = sum(char_counts.values())
    return {"rare": total_count, "rare_percentage": total_count / len(text)}


def count_is_real(pos_count: dict, is_real: dict) -> dict:
    """
    Calculate the percentage of real articles based on the positive count and is_real dictionary.

    Args:
        pos_count (dict): A dictionary containing the positive count for each key.
        is_real (dict): A dictionary indicating whether each key corresponds to a real article (1) or not (0).

    Returns:
        dict: A dictionary containing the percentage of real articles.

    """
    real, unreal = 0, 0
    for key in pos_count:
        if is_real[key] == 1:
            real += pos_count[key]
        else:
            unreal += pos_count[key]
    return {"real_percentage": real / (unreal + real)}


def count_parallelism(word_list: list, conjunctions_list: list) -> dict:
    """
    Counts the number of parallelism occurrences in a given word list.

    Parallelism occurs when a word appears at least three times in the list
    and the positions of its occurrences are within a distance of 5.

    Args:
        word_list (list): A list of words.

    Returns:
        dict: A dictionary containing the count of parallelism occurrences.
            The count is stored under the key "parallelism".
    """
    from collections import defaultdict

    filtered_lst = [item for item in word_list if item in conjunctions_list]
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


def count_metaphor(word_list: list, metaphorical_expressions: list) -> dict:
    """
    Counts the occurrences of metaphorical expressions in a given word list.

    Args:
        metaphorical_expressions:list
        word_list (list): A list of words to search for metaphorical expressions.

    Returns:
        dict: A dictionary containing the count of metaphorical expressions.

    """
    return {"metaphor": sum_occurrences(word_list, metaphorical_expressions)}


def count_fog(avg_sentence_len, complex_words_percentage) -> dict:
    """
    Calculates the Fog Index based on the average sentence length and the percentage of complex words.

    Parameters:
    avg_sentence_len (float): The average length of sentences in a text.
    complex_words_percentage (float): The percentage of complex words in a text.

    Returns:
    dict: A dictionary containing the calculated Fog Index.

    """
    return {"fog": 0.8 * avg_sentence_len + complex_words_percentage}


def segment(collection_read: PymongoCollection) -> None:
    """
    Segments the text in each record of the 'articles' collection in the database.
    Uses the jieba library to perform word segmentation on the 'text' field of each record.
    Updates each record with a new field 'text_seg' containing the segmented text.
    """
    records = list(collection_read.find())
    for record in tqdm(records, desc="Processing records segment", total=len(records)):
        if "text" in record.keys():
            # Perform word segmentation on the 'text' field using jieba library
            text_seg = jieba.lcut(record["text"])
            # Create a new record with the segmented text
            record = {"title": record["title"], "text_seg": text_seg}
            # Update the record in the collection
            collection_read.update_one(
                {"title": record["title"]}, {"$set": record}, upsert=True
            )
        else:
            tqdm.write(f"text field is not found in the title{record}")
    return None


def calculate_all(
    articles: PymongoCollection,
    indexs: PymongoCollection,
    check_field_ignore: str = None,
    limit: int = None,
) -> None:
    rare_word = global_var.get_rare_list()
    real_is_dict = global_var.get_real_pos()
    word_dict = global_var.get_word_dict()
    medical_list = global_var.get_medical_list()
    print("global var are successfully wrote")

    # Start to calculate the index
    bulk_updates = []
    records = articles.find().limit(limit) if limit is not None else articles.find()
    for record in tqdm(
        records,
        desc="Processing records calculate",
        total=limit if limit is not None else 100000,
    ):
        try:
            if (
                check_field_ignore is not None
                and indexs.find_one(
                    {"title": record["title"], check_field_ignore: {"$exists": True}}
                )
                is not None
            ):
                continue
            new_record = {}
            new_record.update(count_html_elements(record["html"]))
            new_record.update(count_about_word(record["text_seg"]))
            new_record.update(count_about_structure(record["text_seg"], word_dict))
            new_record.update(count_metaphor(record["text_seg"], word_dict["metaphor"]))
            new_record.update(
                count_parallelism(record["text_seg"], word_dict["conjunctions"])
            )
            new_record.update(count_medical(record["text_seg"], medical_list))
            new_record.update(count_word_pos(record["text"]))
            new_record.update(count_rare(record["text"], rare_word))
            new_record.update(count_is_real(new_record["pos_count"], real_is_dict))
            new_record.update(count_sentiment(record["sentiment_list"]))
            new_record.update(
                count_about_sentence(record["text"], new_record["pos_list"])
            )
            new_record.update(
                count_fog(
                    new_record["average_sentence_length"], new_record["real_percentage"]
                )
            )
            new_record["character_count"] = len(record["text"])
            new_record["pos_len"] = len(new_record["pos_count"])
            new_record["completely"] = True
            new_record["title"] = record["title"]
            # tqdm.write(str(new_record))
            # indexs.update_one({"title": new_record["title"]}, {"$set": new_record}, upsert=True)
            bulk_updates.append(
                pymongo.UpdateOne(
                    {"title": new_record["title"]}, {"$set": new_record}, upsert=True
                )
            )
        except Exception as e:
            tqdm.write(str(e))
    print("all records were successfully calculated and starting to wrote them")
    if bulk_updates:
        indexs.bulk_write(bulk_updates, ordered=False)
    print("all records were successfully wrote")


if __name__ == "__main__":
    client = pymongo.MongoClient(global_var.client_url)
    database = client[global_var.database_name]
    articles = database["articles"]
    indexs = database["indexs_backend"]
    calculate_all(articles, indexs, None, None)
    # for record in records:
    #     print(count_fog(record["average_length"], record["complex_words_percentage"]))
