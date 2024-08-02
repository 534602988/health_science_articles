import pandas as pd
import global_var
from read_data import write_txt_html_xlsx2db, xlsx2db
import process_mongo
import calculate_index
import sentiment






def main():
    database = process_mongo.get_db()
    data_path = "/workspace/dataset/health/article"
    # write_txt_html_xlsx2db(database,"articles","articles","demand","/workspace/dataset/health/article")
    # process_mongo.delete_duplicates(database,'articles',['title'])
    # process_mongo.delete_duplicates(database,'demand',['title'])
    # calculate_index.segment(database['articles'])
    # print(f'segment are successfully wrote to articles')
    # process_mongo.delete_incomplete_documents(database,'articles',['text'])
    sentiment_dict = global_var.get_sentiment_dict()
    print('Start get sentiment list.....')
    sentiment.get_sentiment_list(sentiment_dict,database['articles'],database['articles'])
    print(f'sentiment list are successfully wrote to articles')
    # calculate_index.calculate_all(database['articles'],database['indexs_backend'])
    # process_mongo.segment(database,'articles')
    # Load the rare words and real words and so on
    



if __name__ == "__main__":
    main()
