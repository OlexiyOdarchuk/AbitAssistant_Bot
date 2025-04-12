import app.database.requests as rq

async def all_abit_len(tg_id:int) -> int:
    data = await rq.get_user_data(tg_id)
    user_abits = [abit for abit in data if abit.user_tg_id == tg_id]
    return len(user_abits)

async def competitors_abit_len(tg_id:int) -> int:
    data = await rq.get_user_data(tg_id)
    user_abits = [abit for abit in data if abit.user_tg_id == tg_id and abit.competitor]
    return len(user_abits)
