import os
import pandas as pd
from read_data import files2db, xlsx2db, segment
from process_mongo import get_db, copy_a2b, insert_with_check
import calculate_index 

DATEBASE = get_db()
DATAPATH = "/workspace/dataset/health_article/article"
RARE_PATH = 'data/rarewords.txt'
with open(RARE_PATH, 'r', encoding='utf-8') as file:
    RARE_WORD = file.read()
IS_REAL_DICT = pd.read_csv("data/pos.csv")

from transformers import T5Tokenizer, T5Config, T5ForConditionalGeneration
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
KEYWORD_MODEL = T5ForConditionalGeneration.from_pretrained(pretrained_model, config=config)
KEYWORD_MODEL.resize_token_embeddings(len(TOKENIZER))
KEYWORD_MODEL.eval()



def write_file2db(parent_folder):
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        # files2db(folder_path, 'text',DATEBASE['articles'])
        # files2db(folder_path, 'html',DATEBASE['articles'])
        xlsx2db(folder_path, DATEBASE["demand"])


def main():
    # write_file2db(DATAPATH)
    # copy_a2b(DATEBASE['articles'],DATEBASE['demand'])
    # segment()
    collection = DATEBASE["articles"].find()
    insert_count = 0
    update_count = 0
    for i, record in enumerate(collection):
        try:
            new_record = calculate_index.keyword_generation(KEYWORD_MODEL,TOKENIZER,record["text"])
            # word_index = count_word_pos(record["text"])
            new_record["title"] = record["title"]
            # print(word_index['pos_list'])
            insert_with_check(DATEBASE["index"], new_record)
            insert_count += 1
        except Exception as e:
            update_count += 1
            print(e)
        if (i + 1) % 1000 == 0:
            print(f"Processed {i + 1} records")
    print(f"Insert count: {insert_count}")
    print(f"Update count: {update_count}")


if __name__ == "__main__":
    
    main()
