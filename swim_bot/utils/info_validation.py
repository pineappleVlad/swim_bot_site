from datetime import datetime, date, time

months_ru = {
    "January": "января",
    "February": "февраля",
    "March": "марта",
    "April": "апреля",
    "May": "мая",
    "June": "июня",
    "July": "июля",
    "August": "августа",
    "September": "сентября",
    "October": "октября",
    "November": "ноября",
    "December": "декабря"
}
day_of_week_ru = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}


def valid_training_date_check(trainer_time_string, trainings_list_of_dict):
    date_time_list = trainer_time_string.split()
    date = date_time_list[0] + " " + date_time_list[1] + " " + date_time_list[2] + " " + date_time_list[3]
    time = date_time_list[4]
    text = ''
    for training in trainings_list_of_dict:
        if (training["date"] == date) and (training["time"] == time):
            text += f"Дата: {training['date']} \n"
            text += f"Время: {training['time']} \n"
            text += f"Тип бассейна: {training['pool_type']} \n"
            text += f"Тренер: {training['trainer_name']} \n"
    return text

def valid_training_date_check_booking(trainer_time_string, trainings_list_of_dict):
    date_time_list = trainer_time_string.split()
    date = date_time_list[0] + " " + date_time_list[1] + " " + date_time_list[2] + " " + date_time_list[3]
    time = date_time_list[4]
    text = ''
    for training in trainings_list_of_dict:
        if (training["date"] == date) and (training["time"] == time):
            text += f"Дата: {training['date']} \n"
            text += f"Время: {training['time']} \n"
            text += f"Тип бассейна: {training['pool_type']} \n"
            text += f"Тренер: {training['trainer_name']} \n"
            text += f"Записанных детей: {training['child_reg_count']}"
    return text

def valid_training_message_text(text_message):
    text_list = text_message.split("\n")
    for text in text_list:
        if 'Дата' in text:
            date_str = text.split(': ')[1].strip()
        elif 'Время' in text:
            time_str = text.split(': ')[1].strip()

    for en_month, ru_month in months_ru.items():
        if ru_month in date_str:
            date_str = date_str.replace(ru_month, en_month)
            break

    for ru_weekday in day_of_week_ru.values():
        if ru_weekday in date_str:
            date_str = date_str.replace(ru_weekday, '')
            break
    date_obj = datetime.strptime(date_str, "%d %B %Yг. ")
    date_result = date_obj.date()

    time_obj = datetime.strptime(time_str, "%H:%M")
    time_result = time_obj.time()
    return date_result, time_result

def valid_training_message_date(date):
    for en_month, ru_month in months_ru.items():
        if ru_month in date:
            date = date.replace(ru_month, en_month).strip()
            break
    date_obj = datetime.strptime(date, "%d %B %Yг.")
    date_result = date_obj.date()
    return date_result


def format_date_for_sorting(date_str):
    not_form_date = date_str.strftime('%Y-%m-%d')
    date_object = datetime.datetime.strptime(not_form_date, "%Y-%m-%d")
    month_rus = months_ru[date_object.strftime("%B")]
    formatted_date = date_object.strftime(f"%d {month_rus} %Yг.")
    return formatted_date

