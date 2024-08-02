import pandas as pd
from pymongo import MongoClient
import pymongo
from tqdm import tqdm
import json
from tqdm import tqdm


def get_db(
    client_url: str = "mongodb://10.48.48.7:27017/", db_name: str = "health_articles"
):
    # Establish a connection to MongoDB
    client = MongoClient(client_url)
    db = client[db_name]
    return db


def copy_a2b(
    database: pymongo.database.Database,
    collection_read_name: str,
    collection_wrote_name: str,
    field: str = "data_availability",
    key: str = "title",
):
    """
    Copies documents from one collection to another, updating or inserting a specified field.

    Args:
        collection_from (pymongo.collection.Collection): The source collection.
        collection_to (pymongo.collection.Collection): The destination collection.
        field (str, optional): The field to update or insert. Defaults to "data_availability".
        key (str, optional): The key to locate the document. Defaults to "title".
    """
    total_documents = database[collection_read_name].count_documents({})
    with tqdm(total=total_documents, desc="Processing documents") as pbar:
        for result in database[collection_read_name].find():
            if field in result.keys():
                database[collection_wrote_name].update_one(
                    {key: result[key]},  # Locate the document based on the key
                    {
                        "$set": {field: result[field]}
                    },  # Update or insert the field and value
                    upsert=True,
                )
            else:
                print(
                    f"Field '{field}' not found in document with {key} = {result.get(key)}"
                )
            pbar.update(1)


def delete_empty_text(
    database: pymongo.database.Database, collection_name: str, field: str = "text"
):
    # Delete documents where the specified field is empty
    database[collection_name].delete_many(
        {"$or": [{field: {"$exists": False}}, {field: None}, {field: ""}]}
    )
    deleted_count = database[collection_name].count_documents(
        {"$or": [{field: {"$exists": False}}, {field: None}, {field: ""}]}
    )
    print(f"Deleted {deleted_count} documents")


def map_fields(
    database: pymongo.database.Database, table_name: str, field_mapping: dict
):
    """
    Maps fields from one collection to another based on a field mapping dictionary.

    Args:
        db (pymongo.database.Database): The MongoDB database.
        table_name (str): The name of the source collection.
        field_mapping (dict): A dictionary mapping old field names to new field names.

    Returns:
        pymongo.collection.Collection: The new collection where the mapped documents are inserted.
    """
    collection = database[table_name]
    total_documents = collection.count_documents({})
    with tqdm(total=total_documents, desc="Processing documents") as pbar:
        for document in collection.find():
            updated_document = {}
            for old_field, new_field in field_mapping.items():
                if old_field in document:
                    updated_document[new_field] = document[old_field]
            new_collection = database[f"{table_name}_copy"]
            new_collection.insert_one(updated_document)
            pbar.update(1)
    return new_collection


def merge(
    database: pymongo.database.Database,
    local_collection_name: str,
    foreign_collection_name: str,
    local_field: str,
    foreign_field: str,
    merge_collection_name: str = "merge",
) -> None:
    """
    Merge data from two MongoDB collections based on specified fields.

    Args:
        db (pymongo.database.Database): The MongoDB database object.
        local_collection_name (str): The name of the local collection.
        foreign_collection_name (str): The name of the foreign collection.
        local_field (str): The field in the local collection to merge on.
        foreign_field (str): The field in the foreign collection to merge on.
        merge_collection_name (str, optional): The name of the merge collection. Defaults to "merge".

    Returns:
        None
    """
    df_local = pd.DataFrame(database[local_collection_name].find())
    df_foreign = pd.DataFrame(database[foreign_collection_name].find())
    merged_df = pd.merge(
        df_local, df_foreign, how="left", left_on=local_field, right_on=foreign_field
    )
    merged_count = len(merged_df)
    if merged_count > 0:
        database[merge_collection_name].insert_many(merged_df.to_dict(orient="records"))
    print(f"Total merged data: {merged_count}")


def delete_incomplete_documents(
    database: pymongo.database.Database,
    collection_name: str,
    required_fields: list = None,
):
    """
    Deletes documents from a collection that do not have all the required fields.

    Args:
        collection (pymongo.collection.Collection): The collection to delete documents from.
        required_fields (list): A list of fields that must be present in the documents.

    Returns:
        None
    """
    collection = database[collection_name]
    if required_fields is None:
        required_fields = collection.find_one().keys()
    filter_query = {"$or": []}
    for field in required_fields:
        filter_query["$or"].append({field: {"$exists": False}})
        filter_query["$or"].append({field: None})
        filter_query["$or"].append({field: ""})
    deleted_count = collection.count_documents(filter_query)
    collection.delete_many(filter_query)
    print(f"Deleted {deleted_count} incomplete documents")


def delete_duplicates(
    database: pymongo.database.Database,
    collection_name: str,
    required_fields: list = None,
):
    """
    Removes duplicate documents from a collection based on specified fields.

    Args:
        collection (pymongo.collection.Collection): The collection to remove duplicates from.
        fields (list): A list of fields to check for duplicates.

    Returns:
        None
    """
    collection = database[collection_name]
    if required_fields is None:
        required_fields = collection.find_one().keys()
    pipeline = [
        {
            "$group": {
                "_id": {field: f"${field}" for field in required_fields},
                "count": {"$sum": 1},
            }
        },
        {"$match": {"count": {"$gt": 1}}},
        {"$project": {"_id": 1}},
    ]
    duplicates = list(collection.aggregate(pipeline))
    for duplicate in duplicates:
        filter_query = {field: duplicate["_id"][field] for field in required_fields}
        collection.delete_many(filter_query)
    print(f"Deleted {len(duplicates)} duplicate documents")


if __name__ == "__main__":
    # Connect to the MongoDB database
    db = get_db()

    # Read the field dictionary from a JSON file
    with open("field_dict.json", "r") as f:
        field_dict = json.load(f)
    map_fields(db, "indexs", field_dict)
    # remove_duplicates(db["articles"],['title'])
    # remove_duplicates(db["demand"],['title'])
    # remove_duplicates(db["indexs_copy"],['title'])
    # remove_duplicates(db["indexs_merge"],['title'])
    merge(db, "demand", "indexs_copy", "title", "title", "indexs_merge")
    # collection = db["articles"]
    # delete_empty_text(collection, field="text")
    # copy_a2b(db["demand"], db["indexs_copy"], "author", "title")
    # collection = db['articles']
    # field_to_remove = 'sentiment_'
    # result = collection.update_many({}, {'$unset': {field_to_remove: ""}})
    # print(f"{result.modified_count} documents updated.")
