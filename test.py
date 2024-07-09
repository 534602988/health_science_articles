import jieba
from collections import Counter

def calculate_unique_word_ratio(text):
    # 使用jieba进行分词
    words = jieba.lcut(text)
    # 计算词频
    word_counts = Counter(words)
    # 计算词频为1的词的数量
    unique_words = [word for word, count in word_counts.items() if count == 1]
    unique_word_count = len(unique_words)
    # 计算所有词的总数量
    total_word_count = len(words)
    # 计算词频为1的词的占比
    unique_word_ratio = unique_word_count / total_word_count if total_word_count > 0 else 0
    
    return unique_word_ratio


def calculate_ratio(text):
    # 使用jieba进行分词
    words = jieba.lcut(text)
    # 计算未去重的词频
    total_word_count = len(words)
    # 计算去重后的词频
    unique_word_count = len(set(words))
    # 计算比值
    ratio = unique_word_count / total_word_count if total_word_count > 0 else 0
    
    return ratio