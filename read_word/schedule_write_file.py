import schedule
import time
import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import pymongo

load_dotenv()

# set parameter
BASTION_HOST = os.getenv('BASTION_HOST')
BASTION_USER = os.getenv('BASTION_USER')
BASTION_PASS = os.getenv('BASTION_PASS')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_AUTH_SOURCE = os.getenv('DB_AUTH_SOURCE')
DB_AUTH_MECH = os.getenv('DB_AUTH_MECH')
DB_NAME = os.getenv('DB_NAME')

LOCAL_BIND_HOST = os.getenv('LOCAL_BIND_HOST')
LOCAL_BIND_PORT = int(os.getenv('LOCAL_BIND_PORT'))

# define ssh tunnel
server = SSHTunnelForwarder(
    BASTION_HOST,
    ssh_username=BASTION_USER,
    ssh_password=BASTION_PASS,
    remote_bind_address=(DB_HOST, DB_PORT),
    local_bind_address=(LOCAL_BIND_HOST, LOCAL_BIND_PORT)
)


# fetch data from database
def fecth_data(db):
    # import itertools
    data = db.object.find()
    keywords = [keyword['keywords'] for keyword in data]
    # keyword_list = list(itertools.chain.from_iterable(keywords))
    keyword_list = sum(keywords, [])
    # print(list(data))
    return keyword_list


# connect database and write file
def job():
    print("I'm working...")
    # tunnel and bind port
    server.start()
    # connection
    connection = pymongo.MongoClient(
        host=server.local_bind_host,
        port=server.local_bind_port,
        username=DB_USER,
        password=DB_PASS,
        authSource=DB_AUTH_SOURCE,
        authMechanism=DB_AUTH_MECH
    )
    db = connection[DB_NAME]
    keyword_list = fecth_data(db)
    print(keyword_list)
    with open('./data/word_list.txt', 'w') as fp:
        for keyword_item in keyword_list:
            fp.write("%s\n" % keyword_item)
    server.stop()


schedule.every().day.at("00:00").do(job)
# schedule.every(1).minutes.do(job)


# write for loop for run all time
while True:
    schedule.run_pending()
    time.sleep(1)
