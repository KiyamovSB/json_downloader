import yaml
import psycopg2
import math
import threading
import os
import datetime


def read_environment_variables():
    global database, user, password, host, port, chunk_size, max_threads, destination_folder, count_chunks_for_log, limit
    database = read_environment_variable("ATA_DATABASE")
    user = read_environment_variable("ATA_USER")
    password = read_environment_variable("ATA_PASSWORD")
    host = read_environment_variable("ATA_HOST")
    port = read_environment_variable("ATA_PORT")
    chunk_size = read_environment_variable("ATA_CHUNK_SIZE")
    max_threads = read_environment_variable("ATA_MAX_THREADS")
    destination_folder = read_environment_variable("ATA_DESTINATION_FOLDER")
    count_chunks_for_log = read_environment_variable("ATA_COUNT_CHUNKS_FOR_LOG")
    limit = read_environment_variable("ATA_LIMIT")


def read_environment_variable(variable):
    if is_read_environment_variables_from_config:
        with open('config.yml') as f:
            template = yaml.safe_load(f)[variable]
    else:
        template = os.environ.get(variable)
    print(f"read environment variable: {variable} = {template}")
    return template


def read_query():
    with open('request.sql', 'r') as f:
        query = f.read()
    return query


def make_cursor():
    con = psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = con.cursor()
    return cursor


def make_db_ids():
    cursor = make_cursor()
    cursor.execute('select source_id, eng_system, master_id from mdm_main.c_party_i where eng_active = 1 limit ' + limit)
    db_ids = cursor.fetchall()
    print(f"count of id set : {len(db_ids)}")
    return db_ids


# пока чанки состоят из 1 сета
def make_chunk_ids(db_ids):
    chunk_ids = db_ids
    # chunk_ids = [db_ids[i:i + int(chunk_size)] for i in range(0, len(db_ids), int(chunk_size))]
    print(f"count of chunk : {len(chunk_ids)}")
    return chunk_ids


def make_directory_path(master_id):
    directory_path_leaven = ('00000' + str(master_id))[-2:]
    directory_path = destination_folder+'/' + directory_path_leaven + '/'
    return directory_path


def write_json_file(source_id, eng_system, master_id, json):
    path = make_directory_path(master_id)
    json_name = eng_system + "=" + source_id + "=" + master_id + ".json"
    full_json_name = path + json_name
    os.makedirs(path, exist_ok=True)
    with open(full_json_name, "w") as file:
        file.write(json)
    return full_json_name


def write_tar_file(master_id, full_json_name):
    # например arc_123_89.tar
    tar_name = "arc_" + ('00000' + str(master_id))[-5:-3] + ('00000' + str(master_id))[-2:] + ".tar"
    os.system(f"tar -rf {tar_name} {full_json_name}")


def delete_json_file(full_json_name):
    os.system(f"rm -f {full_json_name}")


def start_threads(chunk_ids):
    threads = []
    # тут оставляем chunks_for_thread в дробном виде и в дальнейшем используем math.ceil чтобы сбалансированно поделить список для потоков
    chunks_for_thread = len(chunk_ids) / int(max_threads)
    for i in range(int(max_threads)):
        chunk_ids_start = math.ceil(i * chunks_for_thread)
        chunk_ids_end = math.ceil((i + 1) * chunks_for_thread)
        t = threading.Thread(target=start_request, args=(chunk_ids[chunk_ids_start:chunk_ids_end], i,))
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()


def start_request(chunk_ids, thread_number):
    cursor = make_cursor()
    query = read_query()
    for i in range(len(chunk_ids)):
        source_id = str(chunk_ids[i][0])
        eng_system = str(chunk_ids[i][1])
        master_id = str(chunk_ids[i][2])
        cursor.execute(query, [source_id, eng_system])
        rows = cursor.fetchall()
        full_json_name = write_json_file(source_id, eng_system, master_id, rows[0][0])
        write_tar_file(master_id, full_json_name)
        delete_json_file(full_json_name)
        print_count_chunks(thread_number, i)


def print_count_chunks(thread_number, count_done_chunk):
    if count_done_chunk != 0 and count_done_chunk % int(count_chunks_for_log) == 0:
        print(f"thread № {thread_number} done {count_done_chunk} chunks\r")
    return 1


def print_work_time(start_time):
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"{len(chunk_ids)} JSON files done, work time: {days} days, {hours} hours, {minutes} minutes and {seconds} seconds")


is_read_environment_variables_from_config = False

read_environment_variables()
start_time = datetime.datetime.now()
db_ids = make_db_ids()
chunk_ids = make_chunk_ids(db_ids)
start_threads(chunk_ids)
print_work_time(start_time)
