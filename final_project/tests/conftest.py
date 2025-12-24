import os
import random
import string
import sys
from aiogram import Dispatcher
import asyncio
import pytest
import pytest_asyncio

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import User, Chat

from .mocked_bot import MockedBot


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


TEST_USER = User(
    id=12345, is_bot=False, first_name="test", last_name="test",
    username="test", language_code="ru-RU", is_premium=True
)

TEST_USER_CHAT = Chat(
    id=1234, type="private", username=TEST_USER.username,
    first_name=TEST_USER.first_name, last_name=TEST_USER.last_name
)

TEST_PHOTO_ID = "1234"

MESSAGE_MAX_LENGTH = 4096

TEST_LOCATION = [55.7522, 37.6156]


@pytest_asyncio.fixture(scope="session")
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture()
def bot():
    return MockedBot()


@pytest.fixture(name="message_text")
def create_random_message_text():
    length = random.randint(1, MESSAGE_MAX_LENGTH)
    return ''.join(random.choices(
        string.ascii_letters + string.digits + string.punctuation + string.whitespace, k=length
    ))


@pytest.fixture(name="user_id")
def get_user_id():
    return TEST_USER.id


@pytest.fixture(name="latitude")
def get_test_latitude():
    return TEST_LOCATION[0]


@pytest.fixture(name="longtitude")
def get_test_longtitude():
    return TEST_LOCATION[1]


@pytest.fixture(name="photo_id")
def get_test_photo_id():
    return TEST_PHOTO_ID


@pytest.fixture(name="state_update")
def get_test_state():
    return {
        "task_state": "waiting_proof",
        "tasks_count": random.randint(0, 100),
        "duration": random.choice([30, 60, 90]),
        "route": "any",
        "walk_id": 123
    }


@pytest.fixture(name="state_for_route")
def get_test_state_for_route_generation():
    return {
        "mood": "Any mood",
        "activity": "Any activivty",
        "duration": random.choice([30, 60, 90]),
    }


@pytest.fixture(name="state_for_task")
def get_test_state_for_task_generation():
    return {
        "mood": "Any mood",
        "activity": "Any activivty",
        "group_size": random.randint(1, 10),
        "task_state": "no_task"
    }


@pytest.fixture(name="route")
def get_test_route():
    return {
        "description": "Any description",
        "total_time_min": 30,
        "points": [
            {"name": "Any name", "walk_time_min": 15, "task": "Any task"},
            {"name": "Any name 2", "walk_time_min": 15, "task": "Any task 2"}
        ]
    }


@pytest.fixture(name="storage_key")
def create_storage_key(bot: MockedBot):
    return StorageKey(chat_id=TEST_USER_CHAT.id, user_id=TEST_USER.id, bot_id=bot.id)
