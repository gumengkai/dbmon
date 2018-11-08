#! /usr/bin/python
# encoding:utf-8
import tools
import base64
import cx_Oracle

def do_collect():
    # 清空旧的备份信息
    sql = 'delete from oracle_backup_info'
    tools.mysql_exec(sql,'')
    sql = 'delete from oracle_backup_piece'
    tools.mysql_exec(sql, '')
    # 取存活Oracle信息
    sql = '''select tags,host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags in
        (select tags from oracle_db where mon_status = 'connected') '''
    oracle_list = tools.mysql_query(sql)
    if oracle_list:
        for oracle in oracle_list:
            tags = oracle[0]
            host = oracle[1]
            port = oracle[2]
            service_name = oracle[3]
            user = oracle[4]
            password = oracle[5]
            password = base64.decodestring(password)
            url = host + ':' + port + '/' + service_name
            conn = cx_Oracle.connect(user, password, url)
            oracle_collector = OracleBackupoInfo(tags, conn)
            oracle_collector.collect_data()

class OracleBackupoInfo(object):
    def __init__(self,tags,conn):
        self.tags = tags
        self.conn  = conn

    def collect_backup_setup_info(self):
        sql = """select
                            bs_key, recid, stamp,
                            to_char(start_time, 'yyyy-mm-dd hh24:mi:ss'),
                            to_char(completion_time, 'yyyy-mm-dd hh24:mi:ss'),
                            elapsed_seconds, output_bytes,
                            case when backup_type = 'D' then 'DB FULL'
                                 when backup_type = 'L' then 'ARCHIVELOG'
                                 when backup_type = 'I' then 'DB INCR'
                                 else backup_type
                                 end as backup_type,
                            'SUCCESS' as status
                        from v$backup_set_details
                """
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def collect_backup_info(self):
        sql = ''' SELECT A.RECID "BACKUP SET",A.SET_STAMP,DECODE(B.INCREMENTAL_LEVEL, '',DECODE(BACKUP_TYPE, 'L', 'Archivelog', 'Full'),1,'Incr-1Level',0,'Incr-0Level',B.INCREMENTAL_LEVEL),B.CONTROLFILE_INCLUDED ,DECODE(A.STATUS,'A','AVAILABLE','D','DELETED','X','EXPIRED','ERROR') "STATUS",A.DEVICE_TYPE ,to_char(A.start_time, 'yyyy-mm-dd hh24:mi:ss'),to_char(A.completion_time, 'yyyy-mm-dd hh24:mi:ss'),A.ELAPSED_SECONDS,A.BYTES / 1024 / 1024 / 1024,A.COMPRESSED,A.TAG,A.HANDLE FROM GV$BACKUP_PIECE A, GV$BACKUP_SET B WHERE A.SET_STAMP = B.SET_STAMP AND A.DELETED = 'NO' ORDER BY A.COMPLETION_TIME DESC '''
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def collect_data(self):
        oracle_backup_set_list = self.collect_backup_setup_info()
        oracle_backup_list = self.collect_backup_info()
        if oracle_backup_set_list:
            for oracle_backup_set in oracle_backup_set_list:
                insert_sql = "insert into oracle_backup_info(tags,BS_KEY,RECID,STAMP,START_TIME,COMPLETE_TIME,ESPLASED_SECONDS,OUTPUT_BYTES,BACKUP_TYPE,STATUS) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (self.tags, oracle_backup_set[0], oracle_backup_set[1], oracle_backup_set[2],
                          oracle_backup_set[3], oracle_backup_set[4], oracle_backup_set[5],
                          oracle_backup_set[6], oracle_backup_set[7],oracle_backup_set[8])
                tools.mysql_exec(insert_sql, values)

        if oracle_backup_list:
            for oracle_backup in oracle_backup_list:
                insert_sql = "insert into oracle_backup_piece(tags,BACKUP_SET,SET_STAMP,BACKUP_TYPE,HAS_CTL,STATUS,DEVICE_TYPE,START_TIME,COMPLETION_TIME,ELAPSED_TIME,SIZE,COMPRESSED,TAG,PATH) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (self.tags, oracle_backup[0], oracle_backup[1], oracle_backup[2],oracle_backup[3], oracle_backup[4], oracle_backup[5],
                          oracle_backup[6], oracle_backup[7], oracle_backup[8],oracle_backup[9],oracle_backup[10],oracle_backup[11],oracle_backup[12])
                tools.mysql_exec(insert_sql, values)



