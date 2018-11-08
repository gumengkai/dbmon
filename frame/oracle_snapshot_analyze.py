#! /usr/bin/python
# encoding:utf-8

import cx_Oracle
import tools

class SnapShotAnalyze(object):
    def __init__(self,tags,conn,snap_info):
        self.tags = tags
        self.conn = conn
        self.snap_info = snap_info
        self.tab_system_event = 'dba_hist_system_event'
        self.dbid = self.snap_info['db_id']
        self.instance_number = self.snap_info['instance_number']


    def collect_snapshot_top_events(self):
        top_events = self.get_oracle_hist_event_top()
        print top_events

    def get_oracle_hist_event_top(self):
        events_end = self.get_oracle_hist_event_by_snap(self.snap_info['end_snap'])
        events_begin = self.get_oracle_hist_event_by_snap(self.snap_info['begin_snap'])

        events_delta = []
        for event_name,event_data in events_end.items():
            begin_event_data = events_begin.get(event_name,{})
            total_waits_delta = event_data['total_waits'] - begin_event_data.get('total_waits', 0)
            time_waited_delta = event_data['time_waited'] - begin_event_data.get('time_waited', 0)

            events_delta.append(dict(
                event_name=event_name,
                wait_class=event_data['wait_class'],
                total_waits=total_waits_delta,
                total_wait_time=time_waited_delta
            ))
        # 降序
        top_events = sorted(events_delta, key=lambda x: x['total_wait_time'], reverse=True)
        return top_events[:20]

    def get_oracle_hist_event_by_snap(self,snap_id):
        if snap_id is None:
            return {}
        sql = """select event_name, wait_class, total_waits, time_waited_micro
                    from %s
                    where dbid = %s
                    and snap_id = %s
                    and instance_number = %s
                    and wait_class != 'Idle'
                """ %(self.tab_system_event,self.dbid,snap_id,self.instance_number)
        cur = self.conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        events = dict()
        for event_name,wait_class,total_waits,time_waited_mivro in res:
            events[event_name] = dict(
                wait_class = wait_class,
                total_waits = total_waits,
                time_waited = time_waited_mivro/1000
            )
        return events

def do_collect(tags,url,user,password,begin_snap,end_snap):
    sql = "select instance_number from v$instance"
    res = tools.oracle_query(url, user, password, sql)
    instance_num = res[0][0]
    sql = "select dbid from v$database"
    res = tools.oracle_query(url, user, password, sql)
    dbid = res[0][0]
    snap_info = dict(
        db_id=dbid,
        instance_number=instance_num,
        begin_snap=begin_snap,
        end_snap=end_snap
    )
    collector = SnapShotAnalyze(tags, conn, snap_info)
    collector.collect_snapshot_top_events()


if __name__ == '__main__':
    tags = 'orcl'
    url = '192.168.48.10:1521/orcl'
    username = 'dbmon'
    password = 'oracle'
    conn = cx_Oracle.connect(username, password, url)
    do_collect(tags,url,username,password,3422,3425)



