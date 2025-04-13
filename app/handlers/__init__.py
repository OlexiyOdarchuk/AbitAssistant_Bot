from aiogram import Dispatcher

from . import common, admin, filtering, viewing, support

def setup_routers(dp: Dispatcher):
    dp.include_router(common.router)
    dp.include_router(admin.router)
    dp.include_router(filtering.router)
    dp.include_router(viewing.router)
    dp.include_router(support.router)
