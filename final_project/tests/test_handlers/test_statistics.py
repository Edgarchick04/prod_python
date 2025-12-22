import pytest
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch

from handlers.statistics import statistics_handler
from handlers.keyboards import MainKeyboard, UserWalksKeyboard
from states.walk_state import StartState


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
    walks_data = "walk data"
    await state.set_state(StartState.user_walks)
    with patch("handlers.statistics.get_walks_data", AsyncMock(return_value=walks_data)) as mock_get_walks_data:
        await statistics_handler(message, state)
        mock_get_walks_data.assert_called_with(
            message.from_user.id
        )
        message.answer.assert_called_with(
            "walk data\nЧто хочешь посмотреть о своих прогулках?",
            reply_markup=UserWalksKeyboard.user_walks_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == StartState.user_walks


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
        "Начни прогулку или посмотри историю прошлых прогулок.",
        reply_markup=MainKeyboard.start_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu


@pytest.mark.asyncio
async def test_statistics_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in ["Назад", "История маршрутов", "Статистика"] else "Any"
    message.location = None
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(StartState.user_walks)
    await statistics_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.user_walks
