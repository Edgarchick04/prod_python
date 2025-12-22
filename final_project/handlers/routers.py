from aiogram import Dispatcher, Router

from . import commands, statistics, walk_prep, walk_process


command_router = Router()
command_router.include_router(commands.command_router)
command_router.include_router(walk_process.command_router)
command_router.include_router(walk_prep.command_router)
command_router.include_router(statistics.command_router)
dp = Dispatcher()
dp.include_router(command_router)
