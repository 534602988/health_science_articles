import os
import pandas as pd
from process_mongo import get_db,insert_with_check
def files2db(folder_path,header,collection):
    folder_name = os.path.basename(folder_path)
    author = folder_name.split('_')[1:]
    author = '_'.join(author)
    records = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt') and file_name.startswith(header):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding='utf-8') as file:
                content = file.read()
                title = file_name.replace('.txt', '').replace(f'{header}_', '')
                record = {header: content, 'title': title, 'author': author}
                insert_with_check(collection,'title',record)
                records.append(record)
    return records

def xlsx2db(folder_path,collection):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_excel(file_path,na_values=['无'], keep_default_na=True)
            df = df.rename(columns={'标题': 'title', '作者': 'author','阅读量':'read'})
            # 假设"打赏人数"列名为 'donation_count'，找到它的索引
            columns = df.columns
            start_index = columns.get_loc('打赏人数')
            end_index = columns.get_loc('有我关心的内容')
            # 获取从打赏人数这一列到最后一列的所有列
            columns_to_check = columns[start_index:end_index+1]
            # 检查这些列是否全为0，并创建一个新列 '数据可用性'
            df['data_availability'] = (df[columns_to_check].sum(axis=1) != 0).astype(int)
            df.fillna(0, inplace=True)
            data_dict = df.to_dict(orient='records')
            for record in data_dict:
                insert_with_check(collection,'title',record)


if __name__ == "__main__":
    database = get_db()
    parent_folder = "/workspace/dataset/health_article/article"
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
    #     contents = files2db(folder_path, 'text')
    #     htmls = files2db(folder_path, 'html')
        xlsx2db(folder_path,database['demand'])