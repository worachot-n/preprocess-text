from pythainlp.corpus import thai_words
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_words
from pythainlp.util import dict_trie


custom_words = {'เรือหลวงอ่างทอง', 'เรือหลวงจักรีนฤเบศร'}

custom_words_list = set(thai_words())
custom_words_list.update(custom_words)
trie = dict_trie(dict_source=custom_words_list)


# Tokenize word
def tokenize(text: str):
    """Function tokenize word."""
    token_text = word_tokenize(
        text, engine='newmm', custom_dict=trie, keep_whitespace=False)
    return token_text
