import time
import random
from datetime import datetime


def gen_new_user_id():
    t = int(time.time())
    e = str(random.randint(0, 2**30)) + str(t)
    return e


def get_query_id_for_search():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    return f"qid{gen_new_user_id()}{formatted_time}"


