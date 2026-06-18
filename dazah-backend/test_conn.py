import psycopg2
try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        dbname='dazah',
        user='postgres',
        password='postgres',
        client_encoding='UTF8'
    )
    print('psycopg2 连接成功!')
    conn.close()
except Exception as e:
    print(f'连接失败: {e}')
