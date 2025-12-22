from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from services.statistics import set_walks_data
from services.task_generator import TaskGenerator

from states.walk_state import WalkState

from .keyboards import TaskKeyboard
from .walk_utils import finish_walk


command_router = Router()
task_generator = TaskGenerator()


@command_router.message(WalkState.in_walk, F.text)
async def in_walk_handler(message: Message, state: FSMContext):
    """Обработчик команд для выполнения заданий во время прогулки"""
    data = await state.get_data()
    task_state = data.get("task_state", "no_task")
    if task_state == "no_task":
        if message.text == "Сгенерировать задание":
            current_task = await task_generator.generate(
                mood=data["mood"],
                activity=data["activity"],
                group_size=data["group_size"]
            )
            await state.update_data({
                "task_state": "task_generated",
                "current_task": current_task
            })
            await message.answer(
                f"Твое задание:\n{current_task}\nВыполнишь?",
                reply_markup=TaskKeyboard.task_start_keyboard
            )
        elif message.text == "Завершить прогулку":
            await finish_walk(message, state)
        else:
            await message.answer(
                "Выбери вариант из предложенных"
            )
    if task_state == "task_generated":
        if message.text == "Да, принять задание":
            await state.update_data({
                "task_state": "task_in_process"
            })
            await message.answer(
                f"Твое задание:\n{data['current_task']}\nГотов сдать?",
                reply_markup=TaskKeyboard.task_in_process_keyboard
            )
        elif message.text == "Сгенерировать другое задание":
            current_task = await task_generator.generate(
                mood=data["mood"],
                activity=data["activity"],
                group_size=data["group_size"]
            )
            await state.update_data({
                "current_task": current_task
            })
            await message.answer(
                f"Твое задание:\n{current_task}\nВыполнишь?",
                reply_markup=TaskKeyboard.task_start_keyboard
            )
        elif message.text == "Завершить прогулку":
            await finish_walk(message, state)
        else:
            await message.answer(
                "Выбери вариант из предложенных"
            )
    if task_state == "task_in_process":
        if message.text == "Cдать задание":
            await state.update_data({
                "task_state": "waiting_proof"
            })
            await message.answer(
                "Отправь фотографию, как подтверждение",
                reply_markup=ReplyKeyboardRemove()
            )
        elif message.text == "Назад":
            await state.update_data({
                "current_task": None,
                "task_state": "no_task"
            })
            await message.answer(
                "Твое задание отменено",
                reply_markup=TaskKeyboard.task_generation_keyboard
            )
        elif message.text == "Завершить прогулку":
            await finish_walk(message, state)
        else:
            await message.answer(
                "Выбери вариант из предложенных"
            )


@command_router.message(WalkState.in_walk, F.photo)
async def task_photo_proof_handler(message: Message, state: FSMContext):
    """Сохраняет фото-подтверждение выполнения задания"""
    data = await state.get_data()
    if data["task_state"] == "waiting_proof":
        photo_proof = message.photo[-1].file_id
        await state.update_data({
            "walk_state": "in_walk",
            "task_state": "no_task",
            "current_task": None,
            "tasks_count": data.get("tasks_count", 0) + 1,
            "task_photo": photo_proof,
            "duration": data["duration"],
            "route": data["route"]
        })
        await set_walks_data(message.from_user.id)
        await message.answer(
            "Круто, задание выполнено!\nХочешь получить новое?",
            reply_markup=TaskKeyboard.task_generation_keyboard
        )
