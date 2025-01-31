import sqlite3
from lexicon.lexicon_ru import LEXICON_RU
from services.sheets import get_data
from utils.image_downloader import save_image
from utils.task_image_creator import generate_task_images_with_template


async def db_start(database: str):
    conn = create_connection(database)
    cursor = conn.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS data_tasks (
        id INTEGER PRIMARY KEY,
        task_number INTEGER,
        task_theme TEXT,
        task_text TEXT,
        task_image TEXT,
        task_answer REAL,
        task_solution TEXT,
        photo_task TEXT,
        photo_solution TEXT
    )
    '''

    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()


def create_connection(database: str):
    conn = sqlite3.connect(database)
    return conn


def load_data_tasks(database: str, google_sheet_key: str, path_images: str):
    conn = create_connection(database)
    count_before = get_record_count(conn)

    data = get_data(google_sheet_key)

    cursor = conn.cursor()
    query = ('INSERT OR IGNORE INTO data_tasks '
             '(id, task_number, task_theme, task_text, task_image, '
             'task_answer, task_solution, photo_task, photo_solution) '
             'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)')

    for row in data[1:]:
        #task_image
        if row[4]:
            row[4] = save_image(row[4], row[0], path_images)

    cursor.executemany(query, data[1:])
    conn.commit()

    count_after = get_record_count(conn)
    cursor.close()

    if count_after > count_before:
        return f'{LEXICON_RU['success_load_data_tasks']} {count_after - count_before} шт'
    else:
        return LEXICON_RU['no_tasks_to_load']


def get_record_count(conn):
    cursor = conn.cursor()
    query = 'SELECT COUNT(*) FROM data_tasks'
    cursor.execute(query)
    count = cursor.fetchone()[0]
    cursor.close()
    return count


def extract_data_as_dicts(tuple_list, keys):
    return [dict(zip(keys, item)) for item in tuple_list]


async def select_data_for_tasks(database: str, path_images: str, template_json_path: str):
    conn = create_connection(database)
    cursor = conn.cursor()

    columns = ['id', 'task_number', 'task_text', 'task_image', 'task_solution', 'photo_task', 'photo_solution']

    query = f'SELECT {", ".join(columns)} FROM data_tasks'

    cursor.execute(query)
    results = cursor.fetchall()

    new_data = generate_task_images_with_template(extract_data_as_dicts(results, columns), path_images, template_json_path)
    update_tasks_in_database(database, new_data)


def update_tasks_in_database(database: str, updated_data: list):
    conn = create_connection(database)
    cursor = conn.cursor()

    # Подготовим запрос на обновление
    update_query = '''
    UPDATE data_tasks
    SET photo_task = ?, photo_solution = ?
    WHERE id = ?
    '''

    for task in updated_data:
        cursor.execute(update_query, (task['photo_task'], task['photo_solution'], task['id']))

    # Сохраняем изменения
    conn.commit()
    # Закрываем соединение
    cursor.close()
    conn.close()
