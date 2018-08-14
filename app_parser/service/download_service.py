from app_parser import redis

KEY_ACTIVE_DOWNLOADS = 'bt:active_ids'


def remember_download(d_id: int):
    redis.sadd(KEY_ACTIVE_DOWNLOADS, d_id)


def forget_download(d_id: int):
    redis.srem(KEY_ACTIVE_DOWNLOADS, d_id)


def forget_all_downloads():
    redis.delete(KEY_ACTIVE_DOWNLOADS)


def get_all_downloads():
    return {int(e) for e in redis.smembers(KEY_ACTIVE_DOWNLOADS)}
