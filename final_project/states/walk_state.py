from aiogram.fsm.state import StatesGroup, State


class WalkState(StatesGroup):
    choosing_duration = State()
    waiting_geo = State()
    route_generation = State()
    route_accessing = State()
    in_walk = State()
    #walk_finished = State()


class StartState(StatesGroup):
    main_menu = State()
    user_walks = State()
