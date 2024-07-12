import os
import pandas as pd
from read_data import files2db, xlsx2db, segment
from process_mongo import get_db, copy_a2b, insert_with_check
import calculate_index 

DATEBASE = get_db()
DATAPATH = "/workspace/dataset/health_article/article"
RARE_PATH = 'data/rarewords.txt'
with open(RARE_PATH, 'r', encoding='utf-8') as file:
    rare_word = file.read()
is_real_dict = pd.read_csv("data/pos.csv").set_index('en')['isreal'].to_dict()

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
            new_record = calculate_index.count_metaphor(record["text_seg"].split(' '))
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
