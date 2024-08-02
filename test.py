import re

# 示例文件名列表
filenames = [
    "html_6.糖尿病遗传吗？直播义诊，有问必答！.txt",
    "html_健康的生活方式预防慢性疾病直播义诊！.txt"
]

# 定义正则表达式模式
pattern = re.compile(r'html_(?:\d+\.)?(.*?)\.txt')

# 提取并打印中间部分
extracted_parts = [pattern.search(filename).group(1) for filename in filenames]
for part in extracted_parts:
    print(part)
