import pandas as pd
from read_data import write_txt_html_xlsx2db, xlsx2db
import process_mongo
import calculate_index






def main():
    database = process_mongo.get_db()
    # write_txt_html_xlsx2db(database,"articles","articles","demand","/workspace/dataset/health/article")
    # process_mongo.delete_duplicates(database,'articles',['title'])
    # process_mongo.delete_duplicates(database,'demand',['title'])
    
    calculate_index.calculate_all(database['articles'],database['indexs_backend'])
    # process_mongo.segment(database,'articles')
    # Load the rare words and real words and so on
    



if __name__ == "__main__":
    main()
