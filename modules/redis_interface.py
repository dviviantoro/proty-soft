import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def set_redis(key, value):
    r.set(key, value)
    print(f"redis set {key}: {value}")

def get_redis(key):
    value = r.get(key)
    return value