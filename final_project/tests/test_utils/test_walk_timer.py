import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from aiogram.fsm.context import FSMContext

from handlers.walk_utils import walk_timer, active_timers
from handlers.keyboards import MainKeyboard, WalkKeyboard
from states.walk_state import StartState, WalkState



@pytest.mark.asyncio
async def test_walk_timer(storage, storage_key, user_id):
    message = AsyncMock()
    message.from_user.id = user_id
    
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    
    await state.set_state(WalkState.in_walk)
    await state.update_data(
        tasks_count=2,
        walk_id=123
    )
    duration = 1
    with patch("handlers.walk_utils.finish_walk_db", AsyncMock()) as mock_finish_db:
        timer_task = asyncio.create_task(walk_timer(message, duration, state))
        active_timers[user_id] = timer_task
        await asyncio.sleep(2)
        mock_finish_db.assert_called_with(123)
        assert message.answer.call_count >= 2
        message.answer.assert_any_call(
            "<b>Время вышло!</b>\n"
            f"Твоя прогулка длительностью {duration} минут завершена."
            f"Ты выполнил 2 заданий\n",
            reply_markup=WalkKeyboard.walk_end_keyboard,
        )
        message.answer.assert_any_call(
            "Что дальше?",
            reply_markup=MainKeyboard.start_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == StartState.main_menu
        assert user_id not in active_timers
