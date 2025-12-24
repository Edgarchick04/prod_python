import pytest
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock

from handlers.commands import start_cmd_handler
from handlers.keyboards import MainKeyboard
from states.walk_state import StartState


@pytest.mark.asyncio
async def test_start_cmd_handler(storage, storage_key):
    message = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await start_cmd_handler(message, state)
    message.answer.assert_called_with(
        "Привет! Я твой помощник для прогулок.\nНачни прогулку или посмотри историю прошлых прогулок.",
        reply_markup=MainKeyboard.start_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu
