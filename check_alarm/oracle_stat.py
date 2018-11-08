#! /usr/bin/python
# encoding:utf-8

import cx_Oracle
import paramiko

def format_stat(label, stat_vals):
    ret = {}
    for i in range(len(label)):
        if ':' in label[i]:
            label_n, idx = label[i].split(':')
            idx = int(idx)
        else:
            label_n, idx = label[i], i

        ret[label_n] = round(stat_vals[i], 2)
    return ret

class Oraclestat(object):
    def __init__(self,conn):
        self.conn = conn
        self.stat = {}

    def get_oracle_stats(self):
        self.get_oracle_mem()


    def get_oracle_pga(self):
        stat_name = 'sga size'
        cur = self.conn.cursor()
        sql = """select value from v$pgastat where name = 'total PGA allocated'
                    """
        cur.execute(sql)
        pga_size, =  cur.fetchone()
        return pga_size/1024/1024


    def get_oracle_sga(self):
        cur = self.conn.cursor()
        sql = """select sum(bytes) from v$sgainfo where name in (
                    'Fixed SGA Size',
                    'Redo Buffers',
                    'Buffer Cache Size',
                    'Shared Pool Size',
                    'Large Pool Size',
                    'Java Pool Size',
                    'Streams Pool Size',
                    'Shared IO Pool Size'
                )
            """
        cur.execute(sql)
        sga_size, = cur.fetchone()
        sql2 = "select bytes from  v$sgainfo where name = 'Granule Size'"
        cur.execute(sql2)
        granu_size, = cur.fetchone()
        return int(sga_size+granu_size-1)/granu_size*granu_size/1024/1024

    def get_oracle_mem(self):
        sga = self.get_oracle_sga()
        pga = self.get_oracle_pga()

        self.stat['sga size'] = sga
        self.stat['pga size'] = pga


if __name__ == '__main__':
    user = 'dbmon'
    password = 'oracle'
    url = '192.168.48.10:1521/orcl'
    conn = cx_Oracle.connect(user, password, url)
    oraclestat = Oraclestat(conn)
    oraclestat.get_oracle_stats()
