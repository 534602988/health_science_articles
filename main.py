from pymongo import MongoClient
import calculate_topic
import global_var
from read_data import write_txt_html_xlsx2db
import process_mongo
import calculate_index


def main():
    # Establish a connection to MongoDB
    client = MongoClient(global_var.client_url)
    database = client[global_var.database_name]
    # process_mongo.fix_unicode(database,'demand')
    articles = database["articles"]
    indexs = database["indexs"]
    demands = database["demands"]
    write_txt_html_xlsx2db(
        database,
        "articles",
        "articles",
        "demands",
        global_var.health_articles_folder_path,
    )
    process_mongo.delete_incomplete_documents(database, "indexs", ["text"])
    print("starting write segment")
    calculate_index.segment(database, "articles")
    print("starting write topic count")
    calculate_topic.count_topic_all(articles, indexs)
    print("topic are successfully wrote")
    print("starting calculate all the other indexs")
    calculate_index.calculate_all(articles, indexs, None)
    print("successfully calculate all the other indexs")
    process_mongo.map_fields(
        database, "indexs", global_var.get_field_map(), "indexs_zh"
    )
    process_mongo.merge(database, "demands", "indexs_zh", "title", "title", "merge")


if __name__ == "__main__":
    main()
