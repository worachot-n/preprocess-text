from collections import Counter


def count_freq(word_list: list):
    freq_count = Counter(word_list)
    freq_dict = [{'word': k, 'count': v} for k, v in dict(freq_count).items()]
    return freq_dict
