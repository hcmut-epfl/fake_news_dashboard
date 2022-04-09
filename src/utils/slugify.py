import re


def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)