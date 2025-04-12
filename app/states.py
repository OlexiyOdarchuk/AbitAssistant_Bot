from aiogram.fsm.state import State, StatesGroup

class States(StatesGroup):
    get_mailing = State()
    init_mailing = State()
    get_support = State()
    init_support = State()
    get_bal = State()
    get_link = State()
    view_all = State()
    view_competition = State()
