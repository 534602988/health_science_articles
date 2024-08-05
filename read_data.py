import os
import re
import traceback
import pandas as pd
import pymongo.collection
import pymongo.database
from process_mongo import get_db
import pymongo
from tqdm import tqdm


def write_txt_html_xlsx2db(database:pymongo.database.Database,txt_collection_name:str,html_collection_name:str,xlsx_collection_name:str,parent_folder: str) -> None:
    """
    Writes files from the specified parent folder to the database.

    Args:
        parent_folder (str): The path of the parent folder containing the files.

    Returns:
        None
    """
    for folder_name in tqdm(os.listdir(parent_folder)):
        folder_path = os.path.join(parent_folder, folder_name)
        files2db(folder_path, "text", database[txt_collection_name])
        files2db(folder_path, "html", database[html_collection_name])
        xlsx2db(folder_path, database[xlsx_collection_name])


def files2db(
    folder_path: str, header: str, collection: pymongo.collection.Collection
) -> None:
    """
    Read text files from a folder and insert the content into a MongoDB collection.

    Args:
        folder_path (str): Path to the folder containing the text files.
        header (str): Header prefix of the text files.
        collection (pymongo.collection.Collection): MongoDB collection to insert the data into.

    Returns:
        None
    """
    title_pattern = re.compile(r'(?:html|text)_(?:\d+\.)?(.*?)\.(?:txt|html)')
    folder_name = os.path.basename(folder_path)
    author = folder_name
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt") and file_name.startswith(header):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r") as file:
                content = file.read()
                title =title_pattern.search(file_name).group(1)
                record = {header: content, "title": title, "author": str(author)}
                try:
                    collection.update_one(
                        {"title": record["title"]}, {"$set": record}, upsert=True
                    )
                except:
                    print(f"wrong{record}")
                    print(traceback.print_exc())


def xlsx2db(folder_path: str, collection: pymongo.collection.Collection) -> None:
    """
    Read Excel files from a folder and insert or update the data in a MongoDB collection.

    Args:
        folder_path (str): The path to the folder containing the Excel files.
        collection (pymongo.collection.Collection): The MongoDB collection to insert or update the data.

    Returns:
        None
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".xlsx"):
            file_path = os.path.join(folder_path, file_name)
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(file_path, na_values=["无"], keep_default_na=True)
            # Rename the columns of the DataFrame
            df = df.rename(
                columns={"标题": "title", "作者": "xlsx_author", "阅读量": "read"}
            )
            columns = df.columns
            # Extract the author from the file path
            df["author"] = os.path.basename(os.path.dirname(file_path))
            # Find the start and end index of the columns to check for data availability
            start_index = columns.get_loc("打赏人数")
            end_index = columns.get_loc("有我关心的内容")
            columns_to_check = columns[start_index : end_index + 1]
            # Calculate the data availability for each row
            df["data_availability"] = (df[columns_to_check].sum(axis=1) != 0).astype(
                int
            )
            # Fill NaN values with 0
            df.fillna(0, inplace=True)
            # Convert the DataFrame to a list of dictionaries
            data_dict = df.to_dict(orient="records")
            # Insert or update each record in the MongoDB collection
            for record in data_dict:
                collection.update_one(
                    {"title": record["title"]}, {"$set": record}, upsert=True
                )



if __name__ == "__main__":
    database = get_db()
    write_txt_html_xlsx2db(database,"articles","articles","demand","/workspace/dataset/health/article")

