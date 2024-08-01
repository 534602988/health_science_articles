
import traceback
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from tqdm import tqdm


# def insert_with_check(self, collection_name: str, record: dict, key:str="title"):
#     collection = self.database[collection_name]
#     try:
#         collection.update_one({key: record[key]}, {"$set": record}, upsert=True)
#     except:
#         print(f"wrong{record}")
#         print(traceback.print_exc())


# class Health_articles_database(Database):
#     def __init__(self,database) -> None:
#         self.database = database

#     def copy_a2b(
#         self,
#         collection_from_name: str,
#         collection_to_name: str,
#         field:str="data_availability",
#         key:str="title"
#     ):
#         # 获取 源表 中的数据
#         collection_from = self.database[collection_from_name]
#         collection_to = self.database[collection_to_name]
#         results = collection_to.find({}, {})
#         for result in collection_from.find():
#             if field in result.keys():
#                 collection_to.update_one(
#                     {key: result[key]},  # 根据 key 来定位文档
#                     {"$set": {field: result[field]}},  # 更新或插入的字段和值
#                     upsert=True,
#                 )
#             else:
#                 print(
#                     f"Field '{field}' not found in document with {key} = {result.get(key)}"
#                 )


def get_db():
    # Establish a connection to MongoDB
    client = MongoClient("mongodb://10.48.48.7:27017/")
    # Create a new database
    db = client["health_articles"]
    # Create a new collection (table)
    return db


def copy_a2b(
    collection_from: Collection,
    collection_to: Collection,
    field: str = "data_availability",
    key: str = "title"
):
    """
    Copies documents from one collection to another, updating or inserting a specified field.

    Args:
        collection_from (pymongo.collection.Collection): The source collection.
        collection_to (pymongo.collection.Collection): The destination collection.
        field (str, optional): The field to update or insert. Defaults to "data_availability".
        key (str, optional): The key to locate the document. Defaults to "title".
    """
    for result in collection_from.find():
        if field in result.keys():
            collection_to.update_one(
                {key: result[key]},  # Locate the document based on the key
                {"$set": {field: result[field]}},  # Update or insert the field and value
                upsert=True,
            )
        else:
            print(
                f"Field '{field}' not found in document with {key} = {result.get(key)}"
            )


def delete_empty_text(collection: Collection, field="text"):
    # Delete documents where the specified field is empty
    collection.delete_many(
        {"$or": [{field: {"$exists": False}}, {field: None}, {field: ""}]}
    )
    deleted_count = collection.count_documents(
        {"$or": [{field: {"$exists": False}}, {field: None}, {field: ""}]}
    )
    print(f"Deleted {deleted_count} documents")


def map_fields(db, table_name: str, field_mapping: dict):
    """
    Maps fields from one collection to another based on a field mapping dictionary.

    Args:
        db (pymongo.database.Database): The MongoDB database.
        table_name (str): The name of the source collection.
        field_mapping (dict): A dictionary mapping old field names to new field names.

    Returns:
        pymongo.collection.Collection: The new collection where the mapped documents are inserted.
    """
    collection = db[table_name]
    total_documents = collection.count_documents({})
    with tqdm(total=total_documents, desc="Processing documents") as pbar:
        for document in collection.find():
            updated_document = {}
            for old_field, new_field in field_mapping.items():
                if old_field in document:
                    updated_document[new_field] = document[old_field]
            new_collection = db[f'{table_name}_copy']
            new_collection.insert_one(updated_document)
            pbar.update(1)
    return new_collection


if __name__ == "__main__":
    # Connect to the MongoDB database
    db = get_db()
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
    map_fields(db,'indexs',field_dict)
    # collection = db["articles"]
    # delete_empty_text(collection, field="text")
    # copy_a2b(db["articles"], db["index_copy"], "text", "title")
    # collection = db['articles']
    # field_to_remove = 'sentiment_'
    # result = collection.update_many({}, {'$unset': {field_to_remove: ""}})
    # print(f"{result.modified_count} documents updated.")
