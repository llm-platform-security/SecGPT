import redis

def get_keys(): 
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0) 

    # Retrieve all keys (use with caution)
    keys = r.keys('*')
    print(keys)
    return r, keys

def get_values(r, key):
    # Get the value of a specific key
    value = r.get(key) 
    print(value)

if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, db=0) 
    # Retrieve all keys (use with caution)
    keys = r.keys('*')
    print(keys)
    r.flushall()
    