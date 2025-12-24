import pytest
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch

from handlers.statistics import statistics_handler, walk_photos_selection_handler
from handlers.keyboards import MainKeyboard, UserWalksKeyboard
from states.walk_state import StartState
from states.user_walks import UserWalksState


@pytest.mark.asyncio
async def test_statistics_get_stats(storage, storage_key, user_id):
    message = AsyncMock()
    message.text = "Статистика"
    message.from_user.id = user_id
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    stats = "statistics"
    await state.set_state(StartState.user_walks)
    with patch("handlers.statistics.get_stats", AsyncMock(return_value=stats)) as mock_get_stats:
        await statistics_handler(message, state)
        mock_get_stats.assert_called_with(
            message.from_user.id
        )
        message.answer.assert_called_with(
            "statistics\nЧто хочешь посмотреть о своих прогулках?",
            reply_markup=UserWalksKeyboard.user_walks_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == StartState.user_walks


@pytest.mark.asyncio
async def test_statistics_get_walks_data(storage, storage_key, user_id):
    message = AsyncMock()
    message.text = "История маршрутов"
    message.from_user.id = user_id
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(StartState.user_walks)
    walks_data = "Any data"
    walks_map = {1: 123, 2: 1234}
    with patch(
        "handlers.statistics.get_walks_data", AsyncMock(return_value=walks_data)
        ) as mock_get_walks_data, patch(
            "handlers.statistics.get_walks_short", AsyncMock(return_value=walks_map)
        ) as mock_get_walks_short:
        await statistics_handler(message, state)
        mock_get_walks_data.assert_called_once_with(message.from_user.id)
        mock_get_walks_short.assert_called_once_with(message.from_user.id)
        message.answer.assert_called_once_with(
            f"{walks_data}\n"
            "📸 **Введи номер прогулки**, чтобы посмотреть фотографии",
            reply_markup=UserWalksKeyboard.user_walks_keyboard,
            parse_mode="Markdown"
        )
        data = await state.get_data()
        assert data["walks_map"] == walks_map
        tmp_state = await state.get_state()
        assert tmp_state == UserWalksState.viewing_photos


@pytest.mark.asyncio
async def test_walk_photos_selection_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await walk_photos_selection_handler(message, state)
    message.answer.assert_called_with(
        "Начни прогулку или посмотри историю прошлых прогулок",
        reply_markup=MainKeyboard.start_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu


@pytest.mark.asyncio
async def test_walk_photo_selection_get_stats(storage, storage_key, user_id):
    message = AsyncMock()
    message.text = "Статистика"
    message.from_user.id = user_id
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    stats = "statistics"
    await state.set_state(StartState.user_walks)
    with patch("handlers.statistics.get_stats", AsyncMock(return_value=stats)) as mock_get_stats:
        await walk_photos_selection_handler(message, state)
        mock_get_stats.assert_called_with(
            message.from_user.id
        )
        message.answer.assert_called_with(
            "statistics\nЧто хочешь посмотреть о своих прогулках?",
            reply_markup=UserWalksKeyboard.user_walks_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == StartState.user_walks


@pytest.mark.asyncio
async def test_walk_photos_get_walks_data(storage, storage_key, user_id):
    message = AsyncMock()
    message.text = "История маршрутов"
    message.from_user.id = user_id
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    with patch("handlers.statistics.statistics_handler", AsyncMock()) as mock_statistics_handler:
        await walk_photos_selection_handler(message, state)
        mock_statistics_handler.assert_called_once_with(message, state)


@pytest.mark.asyncio
async def test_statistics_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await statistics_handler(message, state)
    message.answer.assert_called_with(
        "Начни прогулку или посмотри историю прошлых прогулок",
        reply_markup=MainKeyboard.start_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu
