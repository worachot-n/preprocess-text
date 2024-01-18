import re


def extract_hashtag(text: str):
    hashtag = [re.sub(r"(\W+)$", "", j)
               for j in set([i for i in text.split() if i.startswith("#")])]
    return hashtag
