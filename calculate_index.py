from collections import Counter
from process_mongo import get_db,insert_with_check
import jieba.posseg as pseg
from bs4 import BeautifulSoup

def count_html_elements(html_content):
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    # 统计各类元素的数量
    img_count = len(soup.find_all('img'))
    audio_count = len(soup.find_all('audio'))
    video_count = len(soup.find_all('video'))
    p_count = len(soup.find_all('p'))
    table_count = len(soup.find_all('table'))
    link_count = len(soup.find_all('a'))
    return {
        'images': img_count,
        'audio': audio_count,
        'video': video_count,
        'paragraphs': p_count,
        'tables': table_count,
        'links': link_count
    }
 
    
def count_about_word(words):
    word_counts = Counter(words)
    # 计算词频为1的词的数量
    unique_words = [word for word, count in word_counts.items() if count == 1]
    # index
    unique_word_count = len(unique_words)
    total_word_count = len(words)
    # index
    word_ratio = word_counts / total_word_count if total_word_count > 0 else 0
    word_lengths = [len(word) for word in words]
    # index
    average_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0

def count_word_pos(text):
    # 使用jieba进行分词和词性标注
    words = pseg.cut(text)
    # 统计词性
    pos_counts = {}
    for word, flag in words:
        if flag not in pos_counts:
            pos_counts[flag] = 0
        pos_counts[flag] += 1
    return {'pos':pos_counts}


def get_structure_index(record:dict):
    if 'html' in record.keys():
        result = count_html_elements(record['html'])
        result['title'] = record['title']
        return result

# def get_pos(record:dict):
#     if 'text' in record.keys():
#         result = count_word_pos(record['text'])
#         result['title'] = record['title']
#         return result

if __name__ == "__main__":
    DATABASE = get_db()
    records = DATABASE['articles'].find()
    for record in records:
        print(get_structure_index(record))
        # Rest of the code