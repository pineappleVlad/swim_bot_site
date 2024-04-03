from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USERNAME, DB_PORT
import asyncpg

async def connect_to_db(): # --- production
    db_params = {
        'host': "db",
        'database': DB_NAME,
        'user': DB_USERNAME,
        'password': DB_PASSWORD,
        'port': DB_PORT
    }
    connection = await asyncpg.connect(**db_params)
    return connection

# async def connect_to_db():
#     db_params = {
#         'host': DB_HOST,
#         'database': DB_NAME,
#         'user': DB_USERNAME,
#         'password': DB_PASSWORD,
#         'port': DB_PORT
#     }
#     connection = await asyncpg.connect(**db_params)
#     return connection
async def close_db(connection):
    await connection.close()

async def execute_query(query, params=None):
    connection = await connect_to_db()
    try:
        if params:
            result = await connection.fetch(query, *params)
        else:
            result = await connection.fetch(query)
        return result
    finally:
        await close_db(connection)



async def execute_query_training_register(query, params=None):
    connection = await connect_to_db()
    try:
        if params:
            result = await connection.execute(query, *params)
        else:
            result = await connection.execute(query)
        return result
    finally:
        await close_db(connection)