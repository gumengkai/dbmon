#! /usr/bin/python
# encoding:utf-8

import redis
import re

INFO_KEYS = """
redis_version
uptime_in_days
redis_mode
connected_slaves
connected_clients
role
used_memory
used_memory_rss
keyspace_hits
keyspace_misses"""


CONFIG_KEYS = """
maxmemory"""

INFO_KEYS_SET = set(INFO_KEYS.split())

CONFIG_KEYS_SET = set(CONFIG_KEYS.split())

class Redisstat(object):
    def __init__(self,conn):
        self.conn=conn
        self.db_pattern = re.compile('^db(\d+)$')

    def get_redis_stat(self):
        redis_stat = {}
        redis_stat['info'] = self.get_redis_info()
        return redis_stat

    def get_redis_info(self):
        info = self.conn.info()
        return info

    def get_redis_config(self):
        config =  self.conn.config_get()
        return config

    def get_redis_data(self):
        info = self.get_redis_info()
        total_keys = 0
        res = {'info':{},'stat':{},'config':{}}
        for k,v in info.items():
            if k in INFO_KEYS_SET:
                res['info'][k] = v
            # 统计Key数量
            if self.db_pattern.match(k):
                total_keys += v['keys']
        res['stat']['total_keys'] = total_keys

        # 获取配置信息
        conf = self.get_redis_config()
        for conf_name in CONFIG_KEYS_SET:
            conf_val = conf.get(conf_name)
            res['config'][conf_name] = conf_val

        return res




if __name__ == "__main__":
    conn = redis.StrictRedis(host='192.168.48.60', port=6379)
    redis=Redisstat(conn)
    print redis.get_redis_data()
