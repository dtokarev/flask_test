from typing import Set

from app_parser import redis

KEY_ACTIVE_DOWNLOADS = 'bt:active_ids'


def remember(d_id: int) -> int:
    return redis.sadd(KEY_ACTIVE_DOWNLOADS, d_id)


def forget(d_id: int) -> int:
    return redis.srem(KEY_ACTIVE_DOWNLOADS, d_id)


def forget_all() -> int:
    return redis.delete(KEY_ACTIVE_DOWNLOADS)


def get_all() -> Set[int]:
    return {int(e) for e in redis.smembers(KEY_ACTIVE_DOWNLOADS)}


def count() -> int:
    return len(get_all())
