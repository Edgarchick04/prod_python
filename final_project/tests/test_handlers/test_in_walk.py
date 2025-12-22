import pytest
import random
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from unittest.mock import AsyncMock, patch

from handlers.walk_process import in_walk_handler
from handlers.keyboards import TaskKeyboard
from states.walk_state import WalkState


@pytest.mark.asyncio
async def test_in_walk_generate_task(storage, storage_key, state_for_task):
    message = AsyncMock()
    message.text = "Сгенерировать задание"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.in_walk)
    await state.update_data(state_for_task)
    task = "any task"
    with patch("handlers.walk_process.task_generator.generate", AsyncMock(return_value=task)) as mock_task_generator:
        await in_walk_handler(message, state)
        mock_task_generator.assert_called_with(
            mood=state_for_task["mood"],
            activity=state_for_task["activity"],
            group_size=state_for_task["group_size"]
        )
        message.answer.assert_called_with(
            "Твое задание:\nany task\nВыполнишь?",
            reply_markup=TaskKeyboard.task_start_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == WalkState.in_walk
        data = await state.get_data()
        assert data["task_state"] == "task_generated"
        assert data["current_task"] == "any task"


@pytest.mark.asyncio
async def test_in_walk_finish_without_task(storage, storage_key):
    message = AsyncMock()
    message.text = "Завершить прогулку"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.in_walk)
    await state.update_data(task_state=random.choice(["no_task", "task_generated", "task_in_process"]))
    with patch("handlers.walk_process.finish_walk", AsyncMock()) as mock_finish_walk:
        await in_walk_handler(message, state)
        mock_finish_walk.assert_called_with(
            message, state
        )


@pytest.mark.asyncio
async def test_in_walk_task_generated_accept(storage, storage_key):
    message = AsyncMock()
    message.text = "Да, принять задание"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.in_walk)
    await state.update_data(task_state="task_generated", current_task="any task")
    await in_walk_handler(message, state)
    message.answer.assert_called_with(
        "Твое задание:\nany task\nГотов сдать?",
        reply_markup=TaskKeyboard.task_in_process_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.in_walk
    data = await state.get_data()
    assert data["task_state"] == "task_in_process"


@pytest.mark.asyncio
async def test_in_walk_generate_another_task(storage, storage_key, state_for_task):
    message = AsyncMock()
    message.text = "Сгенерировать другое задание"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.in_walk)
    await state.update_data(state_for_task)
    await state.update_data(task_state="task_generated")
    task = "another task"
    with patch("handlers.walk_process.task_generator.generate", AsyncMock(return_value=task)) as mock_task_generator:
        await in_walk_handler(message, state)
        mock_task_generator.assert_called_with(
            mood=state_for_task["mood"],
            activity=state_for_task["activity"],
            group_size=state_for_task["group_size"]
        )
        message.answer.assert_called_with(
            "Твое задание:\nanother task\nВыполнишь?",
            reply_markup=TaskKeyboard.task_start_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == WalkState.in_walk
        data = await state.get_data()
        assert data["task_state"] == "task_generated"
        assert data["current_task"] == "another task"


@pytest.mark.asyncio
async def test_in_walk_submit_task(storage, storage_key):
    message = AsyncMock()
    message.text = "Cдать задание"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.in_walk)
    await state.update_data(task_state="task_in_process")
    await in_walk_handler(message, state)
    message.answer.assert_called_with(
        "Отправь фотографию, как подтверждение",
        reply_markup=ReplyKeyboardRemove()
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.in_walk
    data = await state.get_data()
    assert data["task_state"] == "waiting_proof"


@pytest.mark.asyncio
async def test_in_walk_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.in_walk)
    await state.update_data(task_state="task_in_process", current_task="any task")
    await in_walk_handler(message, state)
    message.answer.assert_called_with(
        "Твое задание отменено",
        reply_markup=TaskKeyboard.task_generation_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.in_walk
    data = await state.get_data()
    assert data["task_state"] == "no_task"
    assert data["current_task"] is None


@pytest.mark.asyncio
async def test_in_walk_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in [
        "Сгенерировать задание", "Завершить прогулку", "Да, принять задание",
        "Сгенерировать другое задание", "Cдать задание", "Назад"
    ] else "Any"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.in_walk)
    await state.update_data(task_state=random.choice(["no_task", "task_generated", "task_in_process"]))
    await in_walk_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
