from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, Message

from services.statistics import get_stats, get_walks_data
from services.statistics import get_walk_photos, get_walks_short

from states.user_walks import UserWalksState
from states.walk_state import StartState

from .keyboards import MainKeyboard, UserWalksKeyboard


command_router = Router()


@command_router.message(StartState.user_walks)
async def statistics_handler(message: Message, state: FSMContext):
    """Обработчик команд для просмотра прошлых прогулок"""
    if message.text == "Статистика":
        stats = await get_stats(message.from_user.id)
        await message.answer(
            f"{stats}\nЧто хочешь посмотреть о своих прогулках?",
            reply_markup=UserWalksKeyboard.user_walks_keyboard
        )
        await state.set_state(StartState.user_walks)
        return
    if message.text == "История маршрутов":
        walks_data = await get_walks_data(message.from_user.id)

        walks_map = await get_walks_short(message.from_user.id)

        await state.update_data(walks_map=walks_map)

        if not walks_map:
            await message.answer(walks_data)
            return

        await message.answer(
            f"{walks_data}\n"
            "📸 **Введи номер прогулки**, чтобы посмотреть фотографии",
            reply_markup=UserWalksKeyboard.user_walks_keyboard,
            parse_mode="Markdown"
        )
        await state.set_state(UserWalksState.viewing_photos)
    if message.text == "Назад":
        await message.answer(
            "Начни прогулку или посмотри историю прошлых прогулок",
            reply_markup=MainKeyboard.start_keyboard
            )
        await state.set_state(StartState.main_menu)
        return


@command_router.message(UserWalksState.viewing_photos)
async def walk_photos_selection_handler(message: Message, state: FSMContext):
    """Обработчик выбора пользователя в состоянии просмотра фото"""
    if message.text == "Назад":
        await message.answer(
            "Начни прогулку или посмотри историю прошлых прогулок",
            reply_markup=MainKeyboard.start_keyboard
        )
        await state.set_state(StartState.main_menu)
        return

    if message.text == "Статистика":
        stats = await get_stats(message.from_user.id)
        await message.answer(
            f"{stats}\nЧто хочешь посмотреть о своих прогулках?",
            reply_markup=UserWalksKeyboard.user_walks_keyboard
        )
        await state.set_state(StartState.user_walks)
        return

    if message.text == "История маршрутов":
        await statistics_handler(message, state)
        return

    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи только номер прогулки (цифру)")
        return

    data = await state.get_data()
    walks_map = data.get("walks_map", {})

    selected_num = int(message.text)
    walk_id = walks_map.get(selected_num)

    if not walk_id:
        await message.answer(
            "Прогулки с таким номером нет в списке. Попробуй еще раз"
        )
        return

    photos = await get_walk_photos(walk_id)

    if not photos:
        await message.answer(
            f"У прогулки №{selected_num} нет загруженных фотографий 😔"
        )
    else:
        await message.answer(f"Лови фотографии с прогулки №{selected_num}:")

        media_group = []
        for file_id in photos[:10]:
            media_group.append(InputMediaPhoto(media=file_id))

        await message.answer_media_group(media=media_group)

    await message.answer("Можешь ввести номер другой прогулки")
