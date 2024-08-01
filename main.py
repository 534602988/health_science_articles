import json
import os
import pandas as pd
import pymongo
from read_data import xlsx2db
from process_mongo import get_db, insert_with_check, map_fields
import calculate_index
from transformers import T5Tokenizer, T5Config, T5ForConditionalGeneration
from tqdm import tqdm
import traceback


DATAPATH = "/workspace/dataset/health_article/article"
RARE_PATH = "/workspace/project/health_science_articles/data/rarewords.txt"
POS_PATH = "/workspace/project/health_science_articles/data/pos.csv"
WORD_DICT_PATH = "/workspace/project/health_science_articles/data/word_dict.json"
MEDICAL_PATH = "/workspace/project/health_science_articles/chinese_medical_words"
KEYWORD_GENERATION = False





def main():
    DATEBASE = get_db()
    # Switch to use the keyword generation model or not to save the time
    if KEYWORD_GENERATION is True:
        pretrained_model = "../../model/Randeng-T5-784M-MultiTask-Chinese"
        special_tokens = ["<extra_id_{}>".format(i) for i in range(100)]
        TOKENIZER = T5Tokenizer.from_pretrained(
            pretrained_model,
            do_lower_case=True,
            max_length=512,
            truncation=True,
            additional_special_tokens=special_tokens,
        )
        config = T5Config.from_pretrained(pretrained_model)
        KEYWORD_MODEL = T5ForConditionalGeneration.from_pretrained(
            pretrained_model, config=config
        )
        KEYWORD_MODEL.resize_token_embeddings(len(TOKENIZER))
        KEYWORD_MODEL.eval()
    # Load the rare words and real words and so on
    with open(RARE_PATH, "r", encoding="utf-8") as file:
        rare_word = file.read()
    real_df = pd.read_csv(POS_PATH)
    real_is_dict = dict(zip(real_df["en"], real_df["isreal"]))
    with open(WORD_DICT_PATH, "r") as f:
        wordDictionary = json.load(f)
    articles = DATEBASE["articles"]
    indexs = DATEBASE["indexs"]
    medical_list = calculate_index.txt2list(MEDICAL_PATH)
    # Start to calculate the index
    bulk_updates = []
    for record in tqdm(enumerate(articles.find())):
        try:
            new_record = {}
            new_record.update(calculate_index.count_html_elements(record["html"]))
            new_record.update(calculate_index.count_about_word(record["text_seg"]))
            new_record.update({"pos_len": len(record["pos_count"])})
            new_record.update(calculate_index.count_metaphor(record["text_seg"]))
            new_record.update(
                calculate_index.count_about_sentence(record["text"], record["pos_list"])
            )
            new_record.update(
                calculate_index.count_about_dict(record["text_seg"], wordDictionary)
            )
            new_record.update(
                calculate_index.count_is_real(record["pos_count"], real_is_dict)
            )
            new_record.update(calculate_index.count_sentiment(record["sentiment_list"]))
            new_record.update(calculate_index.count_metaphor(record["text_seg"]))
            new_record.update(calculate_index.count_rare(record["text"], rare_word))
            new_record.update(calculate_index.count_parallelism(record["text_seg"]))
            new_record.update(
                calculate_index.count_medical(record["text_seg"], medical_list)
            )
            new_record.update({"character_count": len(record["text"])})
            new_record["title"] = record["title"]
            bulk_updates.append(
                pymongo.UpdateOne(
                    {"title": new_record["title"]}, {"$set": new_record}, upsert=True
                )
            )
        except Exception as e:
            print(traceback.print_exc())
            break
    if bulk_updates:
        indexs.bulk_write(bulk_updates)
    field_dict ={
        "title": "题目",
        'unique_word_percentage':'词汇独特性',
        'word_ratio':'词汇多样性',
        'real_percentage':'词汇密度',
        'pos_count':'词性分布',
        'cohesive':'知识粘性',
        'mark_radio':'标点符号比例',
        'long_sentence_count':'长句比例',
        'short_sentence_count':'短句比例',
        'average_word_length':'平均词长',
        'average_sentence_length':'平均句长',
        'rare_percentage':'生僻词比例',
        'fog':'迷雾指数',
        'sentenced_length_dev':'句子离散度',
        'v_a':'文本活动度',
        'break':'句子破碎度',
        'sentiment_score':'情感倾向',
        'sentiment_variety':'情感多样性',
        'parallelism':'排比强度',
        'metaphor':'拟喻强度',
        'assertion':'断言强度',
        'cite':'引用强度',
        'level':'递进强度',
        'turning':'转折强度',
        'concession':'让步强度',
        'medical':'专业强度',
        'total_word_count':'总词数',
        'sentence_count':'总句数',
        'entropy':'信息熵',
        'video':'视频数量',
        'audio':'音频数量',
        'images':'图片数量',
        'links':'链接数量',
        'paragraphs':'段落数量',
        'tables':'表格数量',
        'character_count':'总字数',
        'non_repeating_word_count':'总词数（去重）',
        'pos_len':'词性数量',
    }
    map_fields(DATEBASE,'indexs',field_dict)


if __name__ == "__main__":
    main()
