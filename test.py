def unicode2chr(encoded_str:str)->dict:
    """
    This Python function decodes an encoded string containing Unicode characters into a readable string.
    
    :param encoded_str: The `encoded_str` parameter is a string that contains encoded information. The
    function `unicode2chr` takes this encoded string as input and decodes it to extract author
    information. The encoded string is expected to have a specific format with numerical prefixes and
    hexadecimal encoded characters separated by underscores and hashtags
    :return: The function `unicode2chr` returns a dictionary with two keys: 'author_order' and 'author'.
    The 'author_order' key contains the integer value of the prefix extracted from the input string, and
    the 'author' key contains the decoded string obtained by converting the hexadecimal parts of the
    input string to their corresponding Unicode characters and joining them together.
    """
    # 检查是否为空字符串
    if not encoded_str:
        return (None, "")
    # 提取前缀数字和编码部分
    parts = encoded_str.split('_')
    prefix = int(parts[0])
    encoded_parts = parts[1].split('#U')[1:]
    try:
        decoded_str = ''.join([chr(int(part, 16)) for part in encoded_parts])
    except ValueError:
        decoded_str = ''.join([chr(int(part, 16)) for part in encoded_parts if all(c in '0123456789ABCDEF' for c in part)])
    return {'author_order': prefix, 'author': decoded_str}
