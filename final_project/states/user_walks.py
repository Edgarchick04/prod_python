from aiogram.fsm.state import State, StatesGroup


class UserWalksState(StatesGroup):
    choosing_option = State()
    choosing_walk = State()
    viewing_photos = State()
