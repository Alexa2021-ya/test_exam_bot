import sqlite3
from lexicon.lexicon_ru import LEXICON_RU
from services.sheets import get_data


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


def load_data_tasks(database, google_sheet_key: str):
    conn = create_connection(database)
    count_before = get_record_count(conn)

    data = get_data(google_sheet_key)

    cursor = conn.cursor()
    query = ('INSERT OR IGNORE INTO data_tasks '
             '(id, task_number, task_theme, task_text, task_image, '
             'task_answer, task_solution, photo_task, photo_solution) '
             'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)')

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