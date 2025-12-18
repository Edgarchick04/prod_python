from aiogram.fsm.state import StatesGroup, State


class UserWalksState(StatesGroup):
    choosing_option = State()
