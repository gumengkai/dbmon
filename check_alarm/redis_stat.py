#! /usr/bin/python
# encoding:utf-8

import redis

class Redisstat(object):
    def __init__(self,conn):
        self.conn=conn
        self.info=self.conn.info()

    def get_redis_stat(self):
        redis_stat = {}
        redis_stat['info'] = self.get_redis_info()
        return redis_stat

    def get_redis_info(self):
        return {
            'version':self.info['redis_version'],
            'up_days':self.info['uptime_in_days'],
            'redis_mode':self.info['redis_mode'],
            'slaves':self.info['connected_slaves'],
            'connection_clients':self.info['connected_clients'],
            'role':self.info['role'],
            'mem_used':round(float(self.info['used_memory'])/1024/1024,2),
            'mem_used_rss':round(float(self.info['used_memory_rss'])/1024/1024,2)
        }

if __name__ == "__main__":
    conn = redis.StrictRedis(host='192.168.48.60', port=6379)
    redis=Redisstat(conn)
    print redis.get_redis_stat()