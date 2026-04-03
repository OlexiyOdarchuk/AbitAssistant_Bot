# Simple in-memory cache to store parsing results for users
# Key: tg_id (int)
# Value: dict (filtered data)

_results = {}


def save_result(tg_id: int, data: dict):
    _results[tg_id] = data


def get_result(tg_id: int) -> dict:
    return _results.get(tg_id)


def clear_result(tg_id: int):
    if tg_id in _results:
        del _results[tg_id]
