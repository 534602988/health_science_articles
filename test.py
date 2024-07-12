import string

def find_elements_with_conditions(lst):
    from collections import defaultdict

    # 排除标点符号和数字
    filtered_lst = [item for item in lst if not isinstance(item, int) and item not in string.punctuation]

    # 记录每个元素出现的位置
    positions = defaultdict(list)
    for idx, value in enumerate(filtered_lst):
        positions[value].append(idx)
    
    result = []
    
    # 检查每个元素的出现位置
    for value, pos_list in positions.items():
        if len(pos_list) >= 3:
            count = 0
            for i in range(len(pos_list) - 1):
                for j in range(i + 1, len(pos_list)):
                    if pos_list[j] - pos_list[i] < 10:
                        count += 1
                        if count >= 3:
                            result.append(value)
                            break
                if count >= 3:
                    break
    
    return result

# 示例列表，包含一些标点符号和数字
lst = ['a', 'b', 'c', '!', 'a', 'b', 1, 'c', 'a', 'b', 'c', '.', 'a', 'b', 'c','!','!','!','!','!','!']
result = find_elements_with_conditions(lst)
print(result)  # 结果应该包含 'a', 'b', 'c'
