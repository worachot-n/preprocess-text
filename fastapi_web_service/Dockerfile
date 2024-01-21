FROM tiangolo/uvicorn-gunicorn:python3.10-slim

WORKDIR .

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]