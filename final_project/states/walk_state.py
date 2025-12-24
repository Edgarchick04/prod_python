from aiogram.fsm.state import State, StatesGroup


class WalkState(StatesGroup):
    choosing_duration = State()
    choosing_mood = State()
    choosing_activity = State()
    choosing_group_size = State()
    waiting_geo = State()
    route_generation = State()
    route_accessing = State()
    in_walk = State()


class StartState(StatesGroup):
    main_menu = State()
    user_walks = State()
