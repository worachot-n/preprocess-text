from pythainlp.corpus.common import (thai_stopwords,
                                     thai_words,
                                     thai_syllables,
                                     thai_family_names,
                                     thai_female_names,
                                     thai_male_names)
from pythainlp.corpus.ttc import word_freqs
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_words
from pythainlp.util import normalize, remove_zw, remove_dangling, dict_trie, isthai
from pythainlp.tag import NER
import re
import string
from typing import Iterable, List


# Word preparation
# Keep words
thaiwords = thai_words()
syllables = thai_syllables()
familyname = thai_family_names()
femalename = thai_female_names()
malename = thai_male_names()

# Remove words
# Thai stop words
stopwords = thai_stopwords()

# Thai frequency word
freqswords = word_freqs()
freq = 1000  # Set frequency
freqsResults = []

for line in list(freqswords):
    if line[1] >= freq:  # More than threshold means frequency
        freqsResults.append(line[0])

# Manual word
manual_word = ['<unk>', '.',  '…', 'a', 'an', 'the', 'b', 'c', 'd', 'e',
               'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
               'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

custom_words_set = set(thai_words())
custom_words_set.update(familyname)
custom_words_set.update(femalename)
custom_words_set.update(malename)


# Clean tweet
# Define emoji Unicode first
emoji = re.compile("["
                   u"\U0001F600-\U0001F64F"  # Emoticons
                   u"\U0001F300-\U0001F5FF"  # Symbols & pictographs
                   u"\U0001F680-\U0001F6FF"  # Transport & map symbols
                   u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
                   u"\U00002500-\U00002BEF"  # Chinese char
                   u"\U00002702-\U000027B0"
                   u"\U00002702-\U000027B0"
                   u"\U000024C2-\U0001F251"
                   u"\U0001f926-\U0001f937"
                   u"\U00010000-\U0010ffff"
                   u"\u2640-\u2642"
                   u"\u2600-\u2B55"
                   u"\u200d"
                   u"\u23cf"
                   u"\u23e9"
                   u"\u231a"
                   u"\ufe0f"  # Dingbats
                   u"\u3030"
                   "]+", flags=re.UNICODE)  # Flag option as Unicode

# Remove (.) out from punctuation string
newPunc = ''.join(set(string.punctuation) - {'.'})

# Define function for text cleansing


def clean_text(text):
    newText = re.sub(
        r'(?:http|ftp|https)://(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', '', text)  # Remove link
    newText = re.sub(emoji, '', newText)  # Remove emoji
    newText = re.sub(r'@([a-zA-Z0-9_]{1,50})', '', newText)  # Remove @username
    newText = re.sub(r'#([a-zA-Z0-9ก-๙_]+)', '', newText)  # Remove hashtag
    newText = re.sub(r'RT', '', newText)  # Remove 'RT' Word from tweet
    # Remove punctuation without (.)
    newText = newText.translate(str.maketrans('', '', newPunc))
    newText = ' '.join(newText.split())  # Keep only one white space
    return newText


# NER function
_thainer = NER(engine="thainer-v2")


def segment(
    text: str,
    taglist: Iterable[str] = [
        "ORGANIZATION",
        "PERSON",
        "PHONE",
        "EMAIL",
        "DATE",
        "TIME",
        "FACILITY",
        "LOCATION",
        "LEN",
        "URL",
        "ZIP",
        "Money",
        "LAW",
    ],
    tagger=_thainer,
) -> List[str]:
    """
    Dictionary-based maximal matching word segmentation, constrained by
    Thai Character Cluster (TCC) boundaries, and combining tokens that are
    parts of the same named-entity.

    :param str text: text to be tokenized into words
    :param list taglist: a list of named entity tags to be used
    :param class tagger: NER tagger engine
    :return: list of words, tokenized from the text
    """
    if not isinstance(text, str):
        return []

    tagged_words = tagger.tag(text, pos=False)

    words = []
    combining_word = ""
    tags = []
    ner_tag = ""
    for idx, (curr_word, curr_tag) in enumerate(tagged_words):
        if curr_tag != "O":
            tag = curr_tag[2:]
        else:
            tag = "O"

        if curr_tag.startswith("B-") and tag in taglist:
            if curr_word != ".":
                combining_word = curr_word
                ner_tag = tag
            else:
                combining_word += curr_word
        elif (
            curr_tag.startswith("I-")
            and combining_word != ""
            and tag in taglist
        ):
            combining_word += curr_word
        elif curr_tag == "O" and combining_word != "":
            words.append(combining_word)
            tags.append(ner_tag)
            # tags.append(tag)
            combining_word = ""
        else:  # if tag is O
            combining_word = ""
        if idx + 1 == len(tagged_words):
            if curr_tag.startswith("B-") and combining_word != "":
                if curr_word != ".":
                    words.append(combining_word)
                    tags.append(ner_tag)
            elif curr_tag.startswith("I-") and combining_word != "":
                words.append(combining_word)
                tags.append(ner_tag)
            else:
                pass

    return words, tags


# Normalize and Remove mistake
def normalize_word(text: str):
    text = normalize(text)
    text = remove_zw(text)
    text = remove_dangling(text)
    return text


# Tokenize word
def tokenize(text: str):
    """Function tokenize word."""
    # read data from file that map volume in docker compose
    with open('./data/word_list.txt', 'r') as fp:
        keyword_list = fp.read().splitlines()
    custom_words_set.update(keyword_list)
    trie = dict_trie(dict_source=custom_words_set)

    text = text.lower()
    text = normalize_word(text)
    text = clean_text(text)
    word_ner, tag_ner = segment(text)
    new_ner = []
    new_text = text
    if word_ner != []:
        for ner in word_ner:
            ner = normalize_word(ner)
            new_text = new_text.replace(ner, "")
            new_ner.append(ner)
    token_text = word_tokenize(
        new_text, engine='newmm', custom_dict=trie, keep_whitespace=False)  # Using 'newmm'
    token_text = [normalize(word) for word in token_text]  # Normalization word
    # Remove Thai stop words
    token_text = [word for word in token_text if not word in stopwords]
    # Remove Thai frequency words
    token_text = [word for word in token_text if not word in freqsResults]
    if isthai(text, ignore_chars="01234567890+-.,"):
        # Keep Thai word and name
        token_text = [
            word for word in token_text if word in thaiwords or word in familyname or word in femalename or word in malename or word in syllables]
    token_text.extend(new_ner)
    # Remove manual_word
    token_text = [word for word in token_text if not word in manual_word]
    return token_text, word_ner
