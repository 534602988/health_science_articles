import os
from read_data import files2db, xlsx2db
from process_mongo import get_db,copy_a2b
DATEBASE = get_db()
DATAPATH = "/workspace/dataset/health_article/article"


def write_file2db(parent_folder):
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        # files2db(folder_path, 'text',DATEBASE['articles'])
        # files2db(folder_path, 'html',DATEBASE['articles'])
        xlsx2db(folder_path,DATEBASE['demand'])
        
        

def main():
    # write_file2db(DATAPATH)
    copy_a2b(DATEBASE['articles'],DATEBASE['demand'])

if __name__ == "__main__":
    main()