from project.health_science_articles.process_mongo import get_db,insert_with_check

from bs4 import BeautifulSoup

def count_html_elements(html_content):
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 统计各类元素的数量
    img_count = len(soup.find_all('img'))
    audio_count = len(soup.find_all('audio'))
    video_count = len(soup.find_all('video'))
    p_count = len(soup.find_all('p'))
    table_count = len(soup.find_all('table'))
    link_count = len(soup.find_all('a'))
    
    return {
        'images': img_count,
        'audio': audio_count,
        'video': video_count,
        'paragraphs': p_count,
        'tables': table_count,
        'links': link_count
    }


def get_demand_index(db):
    # Your code here
    pass
DATABASE = get_db()
records = DATABASE['articles'].find()
for record in records:
    html = record['html']
    # Parse the HTML
    # Your code here
    parsed_html = count_html_elements(html)
    parsed_html['title'] = record['title']
    print(parsed_html)
    # Rest of the code