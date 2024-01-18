from fastapi import FastAPI
from app.tokenize_word import tokenize
from app.count_freq_word import count_freq
from app.extract_hashtag_word import extract_hashtag
from app.sentiment_text import sentiment
from pydantic import BaseModel


class TextIn(BaseModel):
    full_texts: list[str]


class TextOut(BaseModel):
    process_texts: list


app = FastAPI()


@app.get("/")
def read_root():
    return "server running"


@app.post("/preprocess/")
def preprocess(full_texts: TextIn):
    process_texts = []
    for full_text in full_texts.full_texts:
        word_list = tokenize(full_text)
        freq_list = count_freq(word_list)
        hashtag = extract_hashtag(full_text)
        sentiment_label = sentiment(full_text)
        process_texts.append(
            {"word_list": word_list, "freq": freq_list, "hashtag": hashtag, "sm": sentiment_label})
    return process_texts
