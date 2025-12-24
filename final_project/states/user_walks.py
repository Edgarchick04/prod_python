from aiogram.fsm.state import StatesGroup, State


class UserWalksState(StatesGroup):
    choosing_option = State()
    choosing_walk = State()
    viewing_photos = State()
