from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


class MainKeyboard:
    start_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать прогулку")],
            [KeyboardButton(text="Мои прогулки")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )


class UserWalksKeyboard:
    user_walks_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Статистика")],
            [KeyboardButton(text="История маршрутов")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )


class WalkKeyboard:
    duration_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="30 минут")],
            [KeyboardButton(text="60 минут")],
            [KeyboardButton(text="90 минут")],
            [KeyboardButton(text="В главное меню")]
        ],
        resize_keyboard=True
    )
    mood_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Веселое")],
            [KeyboardButton(text="Грустное")],
            [KeyboardButton(text="Другое")],
            [KeyboardButton(text="Назад")],
            [KeyboardButton(text="В главное меню")],
        ],
        resize_keyboard=True
    )
    activity_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Прогулка")],
            [KeyboardButton(text="Спорт")],
            [KeyboardButton(text="Еда")],
            [KeyboardButton(text="Другое")],
            [KeyboardButton(text="Назад")],
            [KeyboardButton(text="В главное меню")],
        ],
        resize_keyboard=True
    )
    group_size_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1")],
            [KeyboardButton(text="2")],
            [KeyboardButton(text="3")],
            [KeyboardButton(text="4+")],
            [KeyboardButton(text="Назад")],
            [KeyboardButton(text="В главное меню")],
        ],
        resize_keyboard=True
    )
    route_generation_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сгенерировать маршрут")],
            [KeyboardButton(text="Начать прогулку самостоятельно")],
            [KeyboardButton(text="Назад")],
            [KeyboardButton(text="В главное меню")],
        ],
        resize_keyboard=True
    )
    send_geoposition_keboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить геопозицию", request_location=True)],
            [KeyboardButton(text="Назад")],
            [KeyboardButton(text="В главное меню")],
        ],
        resize_keyboard=True
    )
    walk_start_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да, начать прогулку")],
            [KeyboardButton(text="Сгенерировать другой маршрут")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    walk_end_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить прогулку")]
        ],
        resize_keyboard=True
    )


class TaskKeyboard:
    task_generation_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сгенерировать задание")],
            [KeyboardButton(text="Завершить прогулку")]
        ],
        resize_keyboard=True
    )
    task_start_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да, принять задание")],
            [KeyboardButton(text="Сгенерировать другое задание")],
            [KeyboardButton(text="Завершить прогулку")]
        ],
        resize_keyboard=True
    )
    task_in_process_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Cдать задание")],
            [KeyboardButton(text="Завершить прогулку")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
