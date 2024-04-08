import asyncio
from database.db_connection import execute_query, execute_query_training_register
from utils.info_validation import months_ru, format_date_for_sorting, day_of_week_ru
import datetime

async def fio_check(name):
    query = "SELECT name FROM backend_child WHERE name = $1"
    result = await execute_query(query, (name,))
    return bool(result)

async def parent_id_update(chat_id, name): #перезапись айдишника чата
    query = """
    UPDATE backend_child
    SET parent_chat_id = $1
    WHERE name = $2 AND (parent_chat_id IS NULL OR parent_chat_id <> $1);
    """
    result = await execute_query(query, [chat_id, name])
    return bool(result)

async def parent_exists(chat_id):
    query = "SELECT parent_chat_id FROM backend_child WHERE parent_chat_id = $1"
    result = await execute_query(query, (chat_id,))
    return bool(result)


async def child_name_id_write(current_id, child_name):
    # Шаг 1: Удалить все записи с заданным child_name
    delete_query = "DELETE FROM backend_childid WHERE name = $1;"
    await execute_query(delete_query, [child_name])

    delete_db_query = "UPDATE backend_child SET parent_chat_id = $1 WHERE name = $2;"
    await execute_query(delete_db_query, [current_id, child_name])

    # Шаг 2: Проверить существование записи с заданным parent_chat_id
    existing_record_query = "SELECT parent_chat_id FROM backend_childid WHERE parent_chat_id = $1;"
    existing_record = await execute_query(existing_record_query, [current_id])

    if existing_record:  # Шаг 3: Если запись существует, выполнить обновление
        update_query = "UPDATE backend_childid SET name = $1 WHERE parent_chat_id = $2;"
        result = await execute_query(update_query, [child_name, current_id])
    else:  # Шаг 4: Если запись не существует, вставить новую запись
        insert_query = "INSERT INTO backend_childid (parent_chat_id, name) VALUES ($1, $2);"
        result = await execute_query(insert_query, [current_id, child_name])

    return bool(result)

async def get_child_balance(child_name):
    query = "SELECT paid_training_count FROM backend_child WHERE name = $1"
    result = await execute_query(query, (child_name,))
    return result

async def get_child_trainings(child_name):
    query = """
    SELECT t.date, t.time, tr.name AS trainer_name,
    CASE
        WHEN t.pool_type = '1' THEN 'Большой бассейн'
        WHEN t.pool_type = '2' THEN 'Малый бассейн'
    END AS pool_type
    FROM backend_training_children AS tc
    INNER JOIN backend_training AS t ON tc.training_id = t.id
    INNER JOIN backend_child AS c ON tc.child_id = c.id
    INNER JOIN backend_trainers AS tr ON t.trainer_id = tr.id
    WHERE c.name = $1
    """
    result = await execute_query(query, (child_name,))
    formatted_result = []
    for record in result[:9]:
        not_form_date = record['date'].strftime('%Y-%m-%d')
        date_object = datetime.datetime.strptime(not_form_date, "%Y-%m-%d")
        month_rus = months_ru[date_object.strftime("%B")]
        weekday_rus = day_of_week_ru[record['date'].weekday()]
        formatted_date = date_object.strftime(f"%d {month_rus} %Yг. {weekday_rus}")
        formatted_record = {
            'date': formatted_date,
            'time': record['time'].strftime("%H:%M"),
            'pool_type': record['pool_type'],
            'trainer_name': record['trainer_name'],
        }
        formatted_result.append(formatted_record)
    return formatted_result

async def get_child_name(chat_id, table_name):
    query = f"SELECT name FROM {table_name} WHERE parent_chat_id = $1"
    result = await execute_query(query, (chat_id,))
    names = [record['name'] for record in result]
    if len(names) == 1:
        names = names[0]
    return names

async def get_trainings_list(child_name):
    query = """
    SELECT t.date, t.time, tr.name AS trainer_name,
    CASE
        WHEN t.pool_type = '1' THEN 'Большой бассейн'
        WHEN t.pool_type = '2' THEN 'Малый бассейн'
    END AS pool_type
    FROM backend_training AS t
    INNER JOIN backend_trainers AS tr ON t.trainer_id = tr.id
    WHERE t.training_status = '1'
    AND NOT EXISTS (
        SELECT 1
        FROM backend_training_children AS tc
        INNER JOIN backend_child AS c ON tc.child_id = c.id
        WHERE tc.training_id = t.id AND c.name = $1
    )
    """
    training_list = await execute_query(query, (child_name,))
    formatted_result = []
    for record in training_list[:20]:

        not_form_date = record['date'].strftime('%Y-%m-%d')
        date_object = datetime.datetime.strptime(not_form_date, "%Y-%m-%d")
        month_rus = months_ru[date_object.strftime("%B")]
        weekday_rus = day_of_week_ru[record['date'].weekday()]
        formatted_date = date_object.strftime(f"%d {month_rus} %Yг. {weekday_rus}")
        formatted_record = {
            'date': formatted_date,
            'time': record['time'].strftime("%H:%M"),
            'pool_type': record['pool_type'],
            'trainer_name': record['trainer_name'],
            'not_form_date': record['date']
        }
        formatted_result.append(formatted_record)
    sorted_trainings = sorted(formatted_result, key=lambda x: x['not_form_date'])
    return sorted_trainings

async def child_training_register(child_name, date_value, time_value):
    date = datetime.datetime.now()
    child_balance = await get_child_balance(child_name)
    if child_balance[0]['paid_training_count'] == 0:
        return False
    else:
        query_balance = """
        UPDATE backend_child
        SET paid_training_count = paid_training_count - 1
        WHERE name = $1 AND paid_training_count > 0;
        """
        await execute_query_training_register(query_balance, (child_name,))

        query_date = """
        UPDATE backend_child
        SET last_balance_update = $1
        WHERE name = $2;
        """
        await execute_query_training_register(query_date, (date, child_name))

        query_child_register = """
        INSERT INTO backend_training_children (training_id, child_id)
        VALUES (
            (SELECT id FROM backend_training WHERE date = $1
            AND EXTRACT(HOUR FROM time) = EXTRACT(HOUR FROM $2::time)
            AND EXTRACT(MINUTE FROM time) = EXTRACT(MINUTE FROM $2::time)),
            (SELECT id FROM backend_child WHERE name = $3)
        )
        """
        result = await execute_query_training_register(query_child_register, [date_value, time_value, child_name])
        return bool(result)

async def child_training_register_delete(child_name, date_value, time_value):
    date = datetime.datetime.now()
    query_balance = """
    UPDATE backend_child
    SET paid_training_count = paid_training_count + 1
    WHERE name = $1;
    """
    await execute_query_training_register(query_balance, (child_name,))

    query_date = """
    UPDATE backend_child
    SET last_balance_update = $1
    WHERE name = $2;
    """
    await execute_query_training_register(query_date, (date, child_name))

    query_child_register = """
    DELETE FROM backend_training_children
    WHERE training_id = (
        SELECT id FROM backend_training 
        WHERE date = $1 
        AND EXTRACT(HOUR FROM time) = EXTRACT(HOUR FROM $2::time) 
        AND EXTRACT(MINUTE FROM time) = EXTRACT(MINUTE FROM $2::time)
    ) 
    AND child_id = (
        SELECT id FROM backend_child WHERE name = $3
    )
    """
    result = await execute_query_training_register(query_child_register, [date_value, time_value, child_name])
    return bool(result)



async def get_trainings_list_with_date(child_name, date):
    query = """
    SELECT t.date, t.time, tr.name AS trainer_name,
    CASE
        WHEN t.pool_type = '1' THEN 'Большой бассейн'
        WHEN t.pool_type = '2' THEN 'Малый бассейн'
    END AS pool_type
    FROM backend_training AS t
    INNER JOIN backend_trainers AS tr ON t.trainer_id = tr.id
    WHERE t.training_status = '1'
    AND NOT EXISTS (
        SELECT 1
        FROM backend_training_children AS tc
        INNER JOIN backend_child AS c ON tc.child_id = c.id
        WHERE tc.training_id = t.id AND c.name = $1
    )
    AND t.date = $2
    """
    training_list = await execute_query(query, (child_name, date))
    formatted_result = []
    for record in training_list[:20]:
        not_form_date = record['date'].strftime('%Y-%m-%d')
        date_object = datetime.datetime.strptime(not_form_date, "%Y-%m-%d")
        month_rus = months_ru[date_object.strftime("%B")]
        weekday_rus = day_of_week_ru[record['date'].weekday()]
        formatted_date = date_object.strftime(f"%d {month_rus} %Yг. {weekday_rus}")
        formatted_record = {
            'date': formatted_date,
            'time': record['time'].strftime("%H:%M"),
            'pool_type': record['pool_type'],
            'trainer_name': record['trainer_name'],
        }
        formatted_result.append(formatted_record)
    return formatted_result

async def balance_update_db(child_name, trainings_add_count):
    date = datetime.datetime.now()
    query = """
    UPDATE backend_child
    SET paid_training_count = paid_training_count + CAST($1 AS INTEGER)
    WHERE name = $2;
    """
    result = await execute_query(query, (trainings_add_count, child_name))
    query_date = """
    UPDATE backend_child
    SET last_balance_update = $1
    WHERE name = $2;
    """
    await execute_query_training_register(query_date, (date, child_name))
    return bool(result)

async def operation_add_to_story(child_name, date, time, add_training_count):
    query = """
    INSERT INTO backend_balanceoperations (child_name, date, time, add_trainings_count)
    VALUES ($1, $2, $3, $4)
    """
    result = await execute_query(query, [child_name, date, time, int(add_training_count)])
    return bool(result)


async def delete_child_remote(child_name):
    query = """
    UPDATE backend_child
    SET parent_chat_id = NULL
    WHERE name = $1;
    """
    result = await execute_query(query, [child_name])
    return bool(result)


async def get_trainings_list_for_booking(child_name):
    query = """
    SELECT t.date, t.time, tr.name AS trainer_name,
    CASE
        WHEN t.pool_type = '1' THEN 'Большой бассейн'
        WHEN t.pool_type = '2' THEN 'Малый бассейн'
    END AS pool_type,
    (SELECT COUNT(*) 
     FROM backend_training_children AS tc 
     WHERE tc.training_id = t.id) AS child_reg_count
    FROM backend_training AS t
    INNER JOIN backend_trainers AS tr ON t.trainer_id = tr.id
    WHERE t.training_status = '1'
    AND NOT EXISTS (
        SELECT 1
        FROM backend_training_children AS tc
        INNER JOIN backend_child AS c ON tc.child_id = c.id
        WHERE tc.training_id = t.id AND c.name = $1
    )
    """
    training_list = await execute_query(query, (child_name,))
    formatted_result = []
    for record in training_list[:20]:

        not_form_date = record['date'].strftime('%Y-%m-%d')
        date_object = datetime.datetime.strptime(not_form_date, "%Y-%m-%d")
        month_rus = months_ru[date_object.strftime("%B")]
        weekday_rus = day_of_week_ru[record['date'].weekday()]
        formatted_date = date_object.strftime(f"%d {month_rus} %Yг. {weekday_rus}")
        formatted_record = {
            'date': formatted_date,
            'time': record['time'].strftime("%H:%M"),
            'pool_type': record['pool_type'],
            'trainer_name': record['trainer_name'],
            'not_form_date': record['date'],
            'child_reg_count': record['child_reg_count']
        }
        formatted_result.append(formatted_record)
    sorted_trainings = sorted(formatted_result, key=lambda x: x['not_form_date'])
    return sorted_trainings


