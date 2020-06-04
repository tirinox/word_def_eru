from util import *
import mysql.connector
from mysql.connector import MySQLConnection
import os
from tqdm import tqdm
from word_defs import WordDefs


def get_mysql_connect():
    user = os.environ.get('MYSQL_USER', 'tirinox')
    password = os.environ.get('MYSQL_PASSWORD', '123456')
    host = os.environ.get('MYSQL_HOST', '127.0.0.1')
    base = os.environ.get('MYSQL_BASE', 'erudite')
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base)
    return cnx


def n_cross_used_words(sql: MySQLConnection):
    sqlc = sql.cursor()
    sqlc.execute("SELECT COUNT(distinct word) FROM CrossUsedWord")
    result = next(sqlc)[0]
    return result


def add_definition(cursor, word, text, priority, dic, image_url=None):
    cursor.execute("INSERT INTO WordDefinition "
                   "(word, definition, date, dic, imageURL) "
                   "VALUES (%s, %s, %s, %s, %s)",
                   (word, text, priority, dic, image_url))


def add_all_definitions_of_word(defs, cursor):
    if defs and 'defs' in defs and 'word' in defs:
        prior = -10
        word = defs['word']
        for d in defs['defs']:
            add_definition(cursor, word, d['text'], prior, d['dic'])
            prior -= 10


def transfer_all_from_redis_to_mysql(redis: Redis, sql: MySQLConnection):
    sql_cursor = sql.cursor()

    all_wd_keys = WordDefs.all_keys(redis)
    for key in tqdm(all_wd_keys):
        info = WordDefs.decode_db_value(redis.get(key))

        add_all_definitions_of_word(info, sql_cursor)
        sql.commit()


def main():
    redis = get_redis()
    sql = get_mysql_connect()

    transfer_all_from_redis_to_mysql(redis, sql)


if __name__ == '__main__':
    main()
