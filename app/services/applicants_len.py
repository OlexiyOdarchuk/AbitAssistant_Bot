import app.database.requests as rq

async def all_applicant_len(tg_id:int) -> int:
    data = await rq.get_user_data(tg_id)
    user_applicants = [applicant for applicant in data if applicant.user_tg_id == tg_id]
    return len(user_applicants)

async def competitors_applicant_len(tg_id:int) -> int:
    data = await rq.get_user_data(tg_id)
    user_applicants = [applicant for applicant in data if applicant.user_tg_id == tg_id and applicant.competitor]
    return len(user_applicants)
