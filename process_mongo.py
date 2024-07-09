from pymongo import MongoClient
from pymongo.collection import Collection


def insert_with_check(collection: Collection, key, record):
    try:
        collection.update_one({key: record[key]}, {"$set": record}, upsert=True)
    except:
        print(f"wrong{record}")


def get_db():
    # Establish a connection to MongoDB
    client = MongoClient("mongodb://172.16.232.251:27017/")
    # Create a new database
    db = client["health_articles"]
    # Create a new collection (table)
    return db


def copy_a2b(
    collection_to: Collection,
    collection_from: Collection,
    field="data_availability",
    key="title",
):
    # 获取 collection2 中的数据
    results = collection_from.find({}, {})
    for result in results:
        if field in result.keys():
            collection_to.update_one(
                {key: result[key]},  # 根据 key 来定位文档
                {"$set": {field: result[field]}},  # 更新或插入的字段和值
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


if __name__ == "__main__":
    # Connect to the MongoDB database
    db = get_db()

    # collection = db["articles"]
    # delete_empty_text(collection, field="text")
    copy_a2b(db["articles"], db["index"],'pos_list','title')
