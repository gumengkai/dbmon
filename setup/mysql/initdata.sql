/*
Navicat MySQL Data Transfer

Source Server         : dbmon
Source Server Version : 50717
Source Host           : 192.168.48.50:3306
Source Database       : db_monitor

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2019-07-27 16:53:46
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for my_scripts
-- ----------------------------
DROP TABLE IF EXISTS `my_scripts`;
CREATE TABLE `my_scripts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `server_type` varchar(255) DEFAULT NULL,
  `script_type` varchar(255) DEFAULT NULL,
  `content` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of my_scripts
-- ----------------------------
INSERT INTO `my_scripts` VALUES ('1', 'tbs', 'Oracle', 'Monitor', 'set linesize 200\r\nset pages 2000\r\ncol TABLESPACENAME for a30\r\nSELECT  SUBSTR(a.TABLESPACE_NAME,1,30) TablespaceName,\r\n    round(SUM(a.bytes/1024/1024/1024),2)  AS \"Totle_size(G)\",\r\n    round(SUM(NVL(b.free_space1/1024/1024/1024,0)),2) AS \"Free_space(G)\",\r\n    round(SUM(a.bytes/1024/1024/1024),2)-round(SUM(NVL(b.free_space1/1024/1024/1024,0)),2)  AS \"Used_space(G)\",\r\n    ROUND((SUM(a.bytes/1024/1024/1024)-SUM(NVL(b.free_space1/1024/1024/1024,0))) *100/SUM(a.bytes/1024/1024/1024),2) AS \"Used_percent%\",\r\n    round(SUM((case when a.MAXBYTES = 0 then a.bytes else a.MAXBYTES end)/1024/1024/1024),2)                                                                     AS \"Max_size(G)\",\r\n    ROUND((SUM(a.bytes/1024/1024/1024)-SUM(NVL(b.free_space1/1024/1024/1024,0)))*100/SUM((case when a.MAXBYTES = 0 then a.bytes else a.MAXBYTES end)/1024/1024/1024),2) AS \"Max_percent%\"\r\n  FROM dba_data_files a,\r\n    (SELECT SUM(NVL(bytes,0)) free_space1,\r\n      file_id\r\n    FROM dba_free_space\r\n  GROUP BY file_id\r\n   ) b \r\nWHERE a.file_id = b.file_id(+)\r\n GROUP BY a.TABLESPACE_NAME\r\nORDER BY \"Used_percent%\" desc;');
INSERT INTO `my_scripts` VALUES ('2', 'segment_size', 'Oracle', 'Monitor', 'col SEGMENT_TYPE for a15 \r\ncol owner for a10\r\ncol tablespace_name for a10 \r\ncol segment_name for a30\r\nselect owner,\r\n       segment_name,\r\n       segment_type,\r\n       tablespace_name,\r\n       sum(bytes) / 1024 / 1024\r\n  from dba_segments\r\n where segment_name = upper(\'&seg_name\')\r\n group by owner, segment_name, segment_type, tablespace_name;\r\n');
INSERT INTO `my_scripts` VALUES ('3', 'temp_tbs', 'Oracle', 'Monitor', 'set lines 1000 pages 1000\r\nSELECT TABLESPACE_NAME,ROUND(SUM(BYTES_USED)/(1024*1024*1024),2) USED_SPACE,ROUND(SUM(BYTES_FREE)/(1024*1024*1024),2) FREE_SPACE FROM V$TEMP_SPACE_HEADER GROUP BY TABLESPACE_NAME;\r\nset lines 160\r\ncol file_name for a100\r\nselect TABLESPACE_NAME,file_name from dba_temp_files;');
INSERT INTO `my_scripts` VALUES ('4', 'asm_check', 'Oracle', 'Monitor', '--查看磁盘\r\nset linesize 160\r\ncol name for a20 \r\ncol path for a50 \r\ncol FAILGROUP for a20\r\nselect NAME,PATH,FAILGROUP,TOTAL_MB,FREE_MB,STATE from v$asm_disk_stat order by 1;\r\n\r\n--查看磁盘组\r\nset linesize 160\r\ncol name for a20\r\nselect NAME,STATE,TYPE,TOTAL_MB,FREE_MB from v$asm_diskgroup;\r\n\r\n--查看ASM Operation\r\nset linesize 160\r\nselect * from gv$asm_operation; ');
INSERT INTO `my_scripts` VALUES ('5', 'user_create_ddl', 'Oracle', 'Manage', '--获取创建用户脚本及权限\r\nset line 199  \r\nset long 100000 \r\nset pages 1000 \r\nexec DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,\'SQLTERMINATOR\', true);\r\nSELECT (\r\n CASE\r\n   WHEN ((SELECT COUNT(*) FROM dba_users WHERE username = \'&&Username\') > 0)\r\n   THEN dbms_metadata.get_ddl (\'USER\', \'&&Username\')\r\n   ELSE to_clob (\' -- Note: User not found!\')\r\n END ) extracted_ddl\r\nFROM dual\r\nUNION ALL\r\nSELECT (\r\n CASE\r\n   WHEN ((SELECT COUNT(*) FROM dba_ts_quotas WHERE username = \'&&Username\') > 0)\r\n   THEN dbms_metadata.get_granted_ddl( \'TABLESPACE_QUOTA\', \'&&Username\')\r\n   ELSE to_clob (\' -- Note: No TS Quotas found!\')\r\n END )\r\nFROM dual\r\nUNION ALL\r\nSELECT (\r\n CASE\r\n   WHEN ((SELECT COUNT(*) FROM dba_role_privs WHERE grantee = \'&&Username\') > 0)\r\n   THEN dbms_metadata.get_granted_ddl (\'ROLE_GRANT\', \'&&Username\')\r\n   ELSE to_clob (\' -- Note: No granted Roles found!\')\r\n END )\r\nFROM dual\r\nUNION ALL\r\nSELECT (\r\n CASE\r\n   WHEN ((SELECT COUNT(*) FROM dba_sys_privs WHERE grantee = \'&&Username\') > 0)\r\n   THEN dbms_metadata.get_granted_ddl (\'SYSTEM_GRANT\', \'&&Username\')\r\n   ELSE to_clob (\' -- Note: No System Privileges found!\')\r\n END )\r\nFROM dual\r\nUNION ALL\r\nSELECT (\r\n CASE\r\n   WHEN ((SELECT COUNT(*) FROM dba_tab_privs WHERE grantee = \'&&Username\') > 0)\r\n   THEN dbms_metadata.get_granted_ddl (\'OBJECT_GRANT\', \'&&Username\')\r\n   ELSE to_clob (\' -- Note: No Object Privileges found!\')\r\n END )\r\nFROM dual');
INSERT INTO `my_scripts` VALUES ('6', 'wait_event', 'Oracle', 'Monitor', 'col event for a45 \r\nSELECT  inst_id,EVENT, SUM(DECODE(WAIT_TIME, 0, 0, 1)) \"Prev\", SUM(DECODE(WAIT_TIME, 0, 1, 0)) \"Curr\", COUNT(*) \"Tot\" , sum(SECONDS_IN_WAIT) SECONDS_IN_WAIT\r\nFROM GV$SESSION_WAIT\r\nWHERE event NOT\r\nIN (\'smon timer\',\'pmon timer\',\'rdbms ipc message\',\'SQL*Net message from client\',\'gcs remote message\')\r\n    AND event NOT LIKE \'%idle%\'\r\n    AND event NOT LIKE \'%Idle%\'\r\n    AND event NOT LIKE \'%Streams AQ%\'\r\nGROUP BY inst_id,EVENT\r\nORDER BY 1,5 desc;');
INSERT INTO `my_scripts` VALUES ('7', 'session_by_XX', 'Oracle', 'Monitor', 'set line 199 \r\ncol username format a14 \r\ncol event format a35 \r\ncol module format a20 \r\ncol spid format a8 \r\ncol machine format a15\r\ncol B_SESS for a10 \r\n\r\n--根据等待事件查会话\r\nSELECT /*+rule */ sid, s.serial#, spid, event, sql_id, seconds_in_wait ws, row_wait_obj# obj, s.username, s.machine,  BLOCKING_INSTANCE||\'.\'||blocking_session b_sess FROM v$session s, v$process p WHERE event=\'&event_name\' AND s.paddr = p.addr order by 6;\r\n\r\n--根据用户查会话\r\nSELECT /*+rule */ sid, s.serial#, spid, event, sql_id, seconds_in_wait ws, row_wait_obj# obj, s.username, s.machine,  BLOCKING_INSTANCE||\'.\'||blocking_session b_sess FROM v$session s, v$process p WHERE s.username=\'&user_name\' AND s.paddr = p.addr order by 6\r\n\r\n--根据SQL_ID查会话\r\nSELECT /*+rule */ sid, s.serial#, spid, event, sql_id, seconds_in_wait ws, row_wait_obj# obj, s.username, s.machine,  BLOCKING_INSTANCE||\'.\'||blocking_session b_sess FROM v$session s, v$process p WHERE s.sql_id=\'&sql_id\' AND s.paddr = p.addr order by 6\r\n\r\n--根据会话ID查会话详情\r\nSELECT s.sid, s.serial#, spid, event, sql_id, PREV_SQL_ID, seconds_in_wait ws, row_wait_obj# obj, s.username, s.machine, module,blocking_session b_sess,logon_time  FROM v$session s, v$process p WHERE sid = \'&sid\' AND s.paddr = p.addr;\r\n\r\n--查询阻塞会话\r\nselect count(*),blocking_session from v$session where blocking_session is not null group by blocking_session;\r\n\r\n--查询会话的对象信息\r\ncol OBJECT_NAME for a30\r\nselect owner,object_name,subobject_name,object_type from dba_objects where object_id=&oid;');
INSERT INTO `my_scripts` VALUES ('8', 'kill_session', 'Oracle', 'Monitor', 'set line 199 \r\ncol event format a35 \r\n\r\n--杀某个SID会话\r\nSELECT /*+ rule */ sid, s.serial#, \'kill -9 \'||spid, event, blocking_session b_sess FROM v$session s, v$process p WHERE sid=\'&sid\' AND s.paddr = p.addr order by 1;\r\n\r\n--根据SQL_ID杀会话\r\nSELECT /*+ rule */ sid, s.serial#, \'kill -9 \'||spid, event, blocking_session b_sess FROM v$session s, v$process p WHERE sql_id=\'&sql_id\' AND s.paddr = p.addr order by 1;\r\n\r\n--根据等待事件杀会话\r\nSELECT /*+ rule */ sid, s.serial#, \'kill -9 \'||spid, event, blocking_session b_sess FROM v$session s, v$process p WHERE event=\'&event\' AND s.paddr = p.addr order by 1;\r\n\r\n--根据用户杀会话\r\nSELECT /*+ rule */ sid, s.serial#, \'kill -9 \'||spid, event, blocking_session b_sess FROM v$session s, v$process p WHERE username=\'&username\' AND s.paddr = p.addr order by 1;\r\n\r\n--kill所有LOCAL=NO进程\r\nps -ef|grep LOCAL=NO|grep $ORACLE_SID|grep -v grep|awk \'{print $2}\' |xargs kill -9');
INSERT INTO `my_scripts` VALUES ('9', 'lock', 'Oracle', 'Monitor', 'set linesize 180\r\ncol username for a15\r\ncol owner for a15\r\ncol OBJECT_NAME for a30\r\ncol SPID for a10\r\n\r\n--查询某个会话的锁\r\nselect /*+rule*/SESSION_ID,OBJECT_ID,ORACLE_USERNAME,OS_USER_NAME,PROCESS,LOCKED_MODE from gv$locked_object where session_id=&sid;\r\n\r\n--查询TMTX锁\r\nselect /*+rule*/* from v$lock where ctime >100 and type in (\'TX\',\'TM\') order by 3,9;\r\n\r\n--查询数据库中的锁\r\nselect /*+rule*/s.sid,p.spid,l.type,round(max(l.ctime)/60,0) lock_min,s.sql_id,s.USERNAME,b.owner,b.object_type,b.object_name from v$session s, v$process p,v$lock l,v$locked_object o,dba_objects b where  o.SESSION_ID=s.sid and s.sid=l.sid and o.OBJECT_ID=b.OBJECT_ID and s.paddr = p.addr and l.ctime >100 and l.type in (\'TX\',\'TM\',\'FB\') group by s.sid,p.spid,l.type,s.sql_id,s.USERNAME,b.owner,b.object_type,b.object_name order by 9,1,3,4;');
INSERT INTO `my_scripts` VALUES ('10', 'active_session', 'Oracle', 'Monitor', '--活动会话的sql语句\r\nprompt Active session with sql text\r\ncolumn USERNAME format a14\r\nset linesize 200\r\ncolumn EVENT format a30\r\nselect /*+rule */ distinct ses.SID, ses.sql_hash_value, ses.USERNAME, pro.SPID \"OS PID\", substr(stx.sql_text,1,200)\r\nfrom V$SESSION ses\r\n    ,V$SQL stx\r\n    ,V$PROCESS pro \r\nwhere ses.paddr = pro.addr \r\nand ses.status = \'ACTIVE\' \r\nand stx.hash_value = ses.sql_hash_value ;\r\n\r\n--活动会话的等待事件\r\nprompt Active session with wait\r\nselect  /*+rule */ sw.event,sw.wait_time,s.username,s.sid,s.serial#,s.SQL_HASH_VALUE  \r\nfrom v$session s, v$session_wait sw  \r\nwhere s.sid=sw.sid  \r\nand s.USERNAME is not null \r\nand s.status = \'ACTIVE\'; ');
INSERT INTO `my_scripts` VALUES ('11', 'trace', 'Oracle', 'Monitor', '--SQL 10046\r\nalter session set tracefile_identifier=\'enmo10046\';\r\nalter session set events \'10046 trace name context forever, level 12\';\r\nrun your sql;\r\nalter session set events \'10046 trace name context off\';\r\n--如果会话已经运行了，可以用oradebug\r\nconn / as sysdba\r\noradebug setospid 16835\r\noradebug unlimit\r\noradebug event 10046 trace name context forever,level 12\r\noradebug event 10046 trace name context off\r\n\r\n--systemstate dump\r\nsqlplus -prelim / as sysdba\r\noradebug setmypid\r\noradebug unlimit;\r\noradebug dump systemstate 266;\r\n--wait for 1 min\r\noradebug dump systemstate 266;\r\n--wait for 1 min\r\noradebug dump systemstate 266;\r\noradebug tracefile_name;\r\n\r\n--hanganalyze\r\noradebug setmypid\r\noradebug unlimit;\r\noradebug dump hanganalyze 3\r\n--wait for 1 min\r\noradebug dump hanganalyze 3\r\n--wait for 1 min\r\noradebug dump hanganalyze 3\r\noradebug tracefile_name;');
INSERT INTO `my_scripts` VALUES ('12', 'running_job', 'Oracle', 'Monitor', '--查看运行的JOB并中断运行\r\nselect sid,job from dba_jobs_running;  \r\nselect sid,serial# from v$session where sid=\'&sid\';\r\nalter system kill session \'&sid,&serial\';\r\nexec dbms_job.broken(&job,true);');
INSERT INTO `my_scripts` VALUES ('13', 'sess_temp_undo', 'Oracle', 'Monitor', '--temp\r\nCOLUMN tablespace FORMAT A20 \r\nCOLUMN temp_size FORMAT A20 \r\nCOLUMN sid_serial FORMAT A20\r\nCOLUMN username FORMAT A20\r\nCOLUMN program FORMAT A40\r\nSET LINESIZE 200\r\nSELECT b.tablespace,\r\n     ROUND(((b.blocks*p.value)/1024/1024),2)||\'M\' AS temp_size,\r\n     a.sid||\',\'||a.serial# AS sid_serial,\r\n     NVL(a.username, \'(oracle)\') AS  username,\r\n     a.program \r\nFROM   v$session a,\r\n       v$sort_usage b,\r\n       v$parameter p WHERE  p.name  = \'db_block_size\'\r\n AND    a.saddr = b.session_addr \r\nORDER BY b.tablespace, b.blocks;  \r\n\r\n--undo\r\nCOLUMN sid_serial FORMAT A20\r\nCOLUMN username FORMAT A20\r\nCOLUMN program FORMAT A30\r\nCOLUMN undoseg FORMAT A25\r\nCOLUMN undo FORMAT A20\r\nSET LINESIZE 120\r\nSELECT TO_CHAR(s.sid)||\',\'||TO_CHAR(s.serial#) AS sid_serial, \r\n       NVL(s.username, \'(oracle)\') AS username, \r\n       s.program, \r\n       r.name undoseg, \r\n       t.used_ublk * TO_NUMBER(x.value)/1024||\'K\' AS undo \r\nFROM   v$rollname    r, \r\n       v$session     s,\r\n       v$transaction t,\r\n       v$parameter   x \r\nWHERE  s.taddr = t.addr \r\nAND    r.usn   = t.xidusn(+) \r\nAND    x.name  = \'db_block_size\';');
INSERT INTO `my_scripts` VALUES ('14', 'active_sess_2', 'Oracle', 'Monitor', '--判断活跃会话1\r\nselect count(*) ACTIVE_SESSION_COUNT,sum(last_call_et) TOTAL_ACTIVE_TIME ,max(last_call_et) MAX_ACTIVE_TIME,\r\nnvl(event,\'==grouping==\')event, nvl(sql_id,\'==grouping==\') sql_id\r\nfrom v$session\r\nwhere status = \'ACTIVE\' and \r\nnot ( type = \'BACKGROUND\' and state=\'WAITING\' and  wait_class=\'Idle\' )\r\ngroup by cube(event,sql_id)\r\nhaving count(*)>1 or (grouping(event)+grouping(sql_id)=0)\r\norder by 1\r\n/\r\n\r\n--判断活跃会话2（PL/SQL只考虑当前SQL)\r\nselect count(*) ACTIVE_SESSION_COUNT ,sum(sysdate-sql_exec_start)*86400 TOTAL_ACTIVE_TIME ,\r\nmax(sysdate-sql_exec_start)*86400 MAX_ACTIVE_TIME,\r\nnvl(event,\'==grouping==\')event, nvl(sql_id,\'==grouping==\') sql_id\r\nfrom v$session\r\nwhere status = \'ACTIVE\' and \r\nnot ( type = \'BACKGROUND\' and state=\'WAITING\' and  wait_class=\'Idle\' )\r\ngroup by cube(event,sql_id)\r\nhaving count(*)>1 or (grouping(event)+grouping(sql_id)=0)\r\norder by 1\r\n/\r\n\r\n--找到会话对应PL/SQL 对象\r\nselect p.object_name||\'.\'||p.procedure_name plsql_name--,...\r\n from v$session s , dba_procedures p\r\nwhere status = \'ACTIVE\' and \r\n  not ( type = \'BACKGROUND\' and state=\'WAITING\' and  wait_class=\'Idle\' )\r\n  and s.plsql_object_id = p.object_id (+)\r\n  and s.plsql_subprogram_id= p.subprogram_id (+);\r\n  \r\n--找到会话对应的等待对象\r\nselect o.owner||\'.\'||o.object_name waiting_object_name\r\n from v$session s , dba_objects o\r\nwhere s.status = \'ACTIVE\' and \r\n  not ( s.type = \'BACKGROUND\' and state=\'WAITING\' and  wait_class=\'Idle\' )\r\n  and s.row_wait_obj# = o.object_id (+);');
INSERT INTO `my_scripts` VALUES ('15', 'dg', 'Oracle', 'DG', 'set lines 132\r\ncol message for a80\r\ncol timestamp for a20\r\nSELECT ERROR_CODE, SEVERITY, MESSAGE, \r\n       TO_cHAR(TIMESTAMP, \'DD-MON-RR HH24:MI:SS\') TIMESTAMP \r\nFROM V$DATAGUARD_STATUS\r\n WHERE CALLOUT=\'YES\'\r\nAND TIMESTAMP > SYSDATE-1;\r\n\r\nselect THREAD#,sequence#, first_time, next_time, applied from v$archived_log order by 3;\r\n\r\nselect name,database_role,switchover_status from v$database;\r\nselect sequence#, first_time, next_time, applied from v$archived_log order by sequence#; \r\n\r\ncol type for a15\r\nset lines 122\r\nset pages 33\r\ncol item for a20\r\ncol units for a15\r\nselect to_char(start_time, \'DD-MON-RR HH24:MI:SS\') start_time, type,\r\n       item, units, sofar, total, timestamp \r\nfrom v$recovery_progress;\r\n\r\nset lines 132\r\ncol message for a80\r\ncol timestamp for a20\r\nSELECT ERROR_CODE, SEVERITY, MESSAGE, \r\n       TO_cHAR(TIMESTAMP, \'DD-MON-RR HH24:MI:SS\') TIMESTAMP \r\nFROM V$DATAGUARD_STATUS\r\n WHERE CALLOUT=\'YES\'\r\nAND TIMESTAMP > SYSDATE-1;\r\n\r\nselect a.thread#, b.max_available, a.max_applied \r\nfrom\r\n(\r\nselect thread#, max(sequence#) max_applied \r\nfrom gv$archived_log \r\nwhere applied=\'YES\' \r\ngroup by thread# ) a,\r\n(\r\nselect thread#, max(sequence#) max_available \r\nfrom gv$archived_log \r\ngroup by thread# ) b \r\nwhere a.thread#=b.thread#;\r\n\r\n select name,value,datum_time from v$dataguard_stats;\r\n\r\n--ALTER DATABASE RECOVER MANAGED STANDBY DATABASE CANCEL;\r\n--ALTER DATABASE RECOVER MANAGED STANDBY DATABASE DISCONNECT FROM SESSION;\r\n--alter database recover managed standby database using current logfile disconnect from session;');
INSERT INTO `my_scripts` VALUES ('16', 'table_stat', 'Oracle', 'Performance', '--表相关的统计信息\r\n--包含分区、索引、索引字段\r\n--先替换掉下面define值\r\ndefine owner=STEVEN\r\ndefine table_name=AWEN_OGG_TEST\r\n--先替换掉上面define值\r\nset linesize 160\r\ncol DATA_TYPE for a15\r\nset pagesize 10000\r\ncol COLUMN_NAME for a30\r\ncol col for a30\r\nselect TABLE_NAME,    NUM_ROWS,    BLOCKS,    EMPTY_BLOCKS,    CHAIN_CNT,    AVG_ROW_LEN,    GLOBAL_STATS,    SAMPLE_SIZE,   to_char(t.last_analyzed,\'MM-DD-YYYY\') from dba_tables t where    owner = upper(\'&owner\') and table_name = upper(\'&table_name\');\r\nselect COLUMN_NAME, DATA_TYPE,   NUM_DISTINCT,    DENSITY,    NUM_BUCKETS,    NUM_NULLS,    SAMPLE_SIZE,    to_char(t.last_analyzed,\'MM-DD-YYYY\') from dba_tab_columns t where   owner = upper(\'&owner\') and table_name = upper(\'&table_name\');\r\nselect INDEX_NAME,    BLEVEL BLev,    LEAF_BLOCKS,    DISTINCT_KEYS,    NUM_ROWS,    AVG_LEAF_BLOCKS_PER_KEY,    AVG_DATA_BLOCKS_PER_KEY,    CLUSTERING_FACTOR,    to_char(t.last_analyzed,\'MM-DD-YYYY\') from    dba_indexes t where    table_name =  upper(\'&table_name\') and table_owner = upper(\'&owner\');\r\nselect /*+ first_rows use_nl(i,t)*/ i.INDEX_NAME,    i.COLUMN_NAME,    i.COLUMN_POSITION,    decode(t.DATA_TYPE,           \'NUMBER\',t.DATA_TYPE||\'(\'||           decode(t.DATA_PRECISION,                  null,t.DATA_LENGTH||\')\',                  t.DATA_PRECISION||\',\'||t.DATA_SCALE||\')\'),                  \'DATE\',t.DATA_TYPE,                  \'LONG\',t.DATA_TYPE,                  \'LONG RAW\',t.DATA_TYPE,                  \'ROWID\',t.DATA_TYPE,                  \'MLSLABEL\',t.DATA_TYPE,                  t.DATA_TYPE||\'(\'||t.DATA_LENGTH||\')\') ||\' \'||           decode(t.nullable,                  \'N\',\'NOT NULL\',                  \'n\',\'NOT NULL\',                  NULL) col   from     dba_ind_columns i,    dba_tab_columns t where i.index_owner=t.owner and     i.table_name = upper(\'&table_name\') and i.index_owner = upper(\'&owner\') and i.table_name = t.table_name and i.column_name = t.column_name order by index_name,column_position;\r\n\r\n--收集统计信息\r\nexec dbms_stats.gather_table_stats(\'STEVEN\',\'AWEN_OGG_TEST\',degree=>10,cascade=> TRUE,no_invalidate=>false);');
INSERT INTO `my_scripts` VALUES ('17', 'db_time', 'Oracle', 'Performance', '--查询DB Time\r\nSELECT TO_CHAR(a.end_interval_time,\'yyyymmdd hh24\'),\r\n    SUM (a.db_time) inst1_m,\r\n    SUM (b.db_time) inst2_m\r\n  FROM\r\n    (SELECT pre_snap_id,\r\n      snap_id,\r\n      end_interval_time,\r\n      ROUND((value - pre_value) / 1000000 / 60) db_time\r\n    FROM\r\n      (SELECT a.snap_id,\r\n        end_interval_time,\r\n        lag(a.snap_id) over(order by a.snap_id) pre_snap_id,\r\n        value,\r\n        lag(value) over(order by a.snap_id) pre_value\r\n      FROM dba_hist_sys_time_model a,\r\n        dba_hist_snapshot b\r\n      WHERE stat_name      = \'DB time\'\r\n      AND a.dbid           = b.dbid\r\n      AND a.snap_id        = b.snap_id\r\n      AND a.instance_number=b.instance_number\r\n      AND a.dbid           =\r\n        (SELECT dbid FROM v$database\r\n        )\r\n      AND a.instance_number = 1\r\n      )\r\n    WHERE pre_snap_id   IS NOT NULL\r\n  AND end_interval_time>sysdate-30\r\n  ORDER BY snap_id DESC\r\n  ) a,\r\n  (SELECT pre_snap_id,\r\n    snap_id,\r\n    end_interval_time,\r\n    ROUND((value - pre_value) / 1000000 / 60) db_time\r\n  FROM\r\n    (SELECT a.snap_id,\r\n      end_interval_time,\r\n      lag(a.snap_id) over(order by a.snap_id) pre_snap_id,\r\n      value,\r\n      lag(value) over(order by a.snap_id) pre_value\r\n    FROM dba_hist_sys_time_model a,\r\n      dba_hist_snapshot b\r\n    WHERE stat_name      = \'DB time\'\r\n    AND a.dbid           = b.dbid\r\n    AND a.snap_id        = b.snap_id\r\n    AND a.instance_number=b.instance_number\r\n    AND a.dbid           =\r\n      (SELECT dbid FROM v$database\r\n      )\r\n    AND a.instance_number = 2\r\n    )\r\n  WHERE pre_snap_id   IS NOT NULL\r\n  AND end_interval_time>sysdate-30\r\n  ORDER BY snap_id DESC\r\n  ) b\r\nWHERE a.snap_id=b.snap_id(+)\r\nGROUP BY TO_CHAR(a.end_interval_time,\'yyyymmdd hh24\')\r\nORDER BY TO_CHAR(a.end_interval_time,\'yyyymmdd hh24\');');
INSERT INTO `my_scripts` VALUES ('18', 'log_switch', 'Oracle', 'Performance', 'col LOG_HOUR format a12\r\nselect to_char(first_time, \'YYYY-mm-dd\') LOG_DATE,\r\n       to_char(first_time, \'HH24\') LOG_HOUR,\r\n       count(*) SWITCHES\r\n  from v$loghist\r\n group by to_char(first_time, \'YYYY-mm-dd\'), to_char(first_time, \'HH24\')\r\n order by 1, 2;');
INSERT INTO `my_scripts` VALUES ('19', 'sess_longops', 'Oracle', 'Performance', 'set linesize 180\r\ncol opname format a20\r\ncol target format a45\r\ncol units format a10\r\ncol time_remaining format 99990 heading Remaining[s]\r\ncol bps format 9990.99 heading [Units/s]\r\ncol fertig format 90.99 heading \"complete[%]\"\r\nselect sid,\r\n       opname,\r\n       target,\r\n       sofar,\r\n       totalwork,\r\n       units,\r\n       (totalwork-sofar)/time_remaining bps,\r\n       time_remaining,\r\n       sofar/totalwork*100 fertig\r\nfrom   v$session_longops\r\nwhere  time_remaining > 0;');
INSERT INTO `my_scripts` VALUES ('20', 'sql_plan', 'Oracle', 'Performance', '--explain查看SQL执行计划\r\nEXPLAIN  PLAN FOR select count(*) from steven.AWEN_OGG_TEST;\r\nselect * from table(dbms_xplan.display());\r\n\r\n--查看AWR和CURSOR中的执行计划\r\nselect * from table(dbms_xplan.display_awr(\'&sqlid\'));\r\nselect * from table(dbms_xplan.display_cursor(\'&sqlid\'));\r\n\r\n--查看内存中的执行计划\r\nselect \'| Operation                         |Object Name                    |  Rows | Bytes|   Cost |\'\r\nas \"Explain Plan in library cache:\" from dual\r\nunion all\r\nselect rpad(\'| \'||substr(lpad(\' \',1*(depth-1))||operation||\r\n      decode(options, null,\'\',\' \'||options), 1, 35), 36, \' \')||\'|\'||\r\n      rpad(decode(id, 0, \'----------------------------\',\r\n      substr(decode(substr(object_name, 1, 7), \'SYS_LE_\', null, object_name)\r\n      ||\' \',1, 30)), 31, \' \')||\'|\'|| lpad(decode(cardinality,null,\'  \',\r\n      decode(sign(cardinality-1000), -1, cardinality||\' \',\r\n      decode(sign(cardinality-1000000), -1, trunc(cardinality/1000)||\'K\',\r\n      decode(sign(cardinality-1000000000), -1, trunc(cardinality/1000000)||\'M\',\r\n      trunc(cardinality/1000000000)||\'G\')))), 7, \' \') || \'|\' ||\r\n      lpad(decode(bytes,null,\' \',\r\n      decode(sign(bytes-1024), -1, bytes||\' \',\r\n      decode(sign(bytes-1048576), -1, trunc(bytes/1024)||\'K\',\r\n      decode(sign(bytes-1073741824), -1, trunc(bytes/1048576)||\'M\',\r\n      trunc(bytes/1073741824)||\'G\')))), 6, \' \') || \'|\' ||\r\n      lpad(decode(cost,null,\' \', decode(sign(cost-10000000), -1, cost||\' \',\r\n      decode(sign(cost-1000000000), -1, trunc(cost/1000000)||\'M\',\r\n      trunc(cost/1000000000)||\'G\'))), 8, \' \') || \'|\' as \"Explain plan\"\r\n from v$sql_plan sp\r\n where sp.hash_value=&hash_value or sp.sql_id=\'&sqlid\';\r\n\r\n--查看历史执行计划\r\nselect distinct SQL_ID,PLAN_HASH_VALUE,to_char(TIMESTAMP,\'yyyymmdd hh24:mi:ss\') TIMESTAMP\r\n from dba_hist_sql_plan\r\n where SQL_ID=\'&sqlid\' order by TIMESTAMP;');
INSERT INTO `my_scripts` VALUES ('21', 'table_index', 'Oracle', 'Performance', '--查看表的索引\r\nselect col.table_owner \"table_owner\",\r\nidx.table_name \"table_name\",\r\ncol.index_owner \"index_owner\",\r\nidx.index_name \"index_name\",\r\nuniqueness \"uniqueness\",\r\nstatus,\r\ncolumn_name \"column_name\",\r\ncolumn_position\r\nfrom dba_ind_columns col, dba_indexes idx\r\nwhere col.index_name = idx.index_name\r\nand col.table_name = idx.table_name and col.table_owner = idx.table_owner\r\nand col.table_owner=\'&owner\'\r\nand col.table_name=\'&table_name\')\r\norder by idx.table_type,\r\nidx.table_name,\r\nidx.index_name,\r\ncol.table_owner,\r\ncolumn_position;');
INSERT INTO `my_scripts` VALUES ('22', '表碎片', 'Oracle', 'Monitor', 'SELECT TABLE_NAME,(BLOCKS*8192/1024/1024)\"理论大小M\", \r\n(NUM_ROWS*AVG_ROW_LEN/1024/1024/0.9)\"实际大小M\", \r\nround((NUM_ROWS*AVG_ROW_LEN/1024/1024/0.9)/(BLOCKS*8192/1024/1024),3)*100||\'%\' \"实际使用率%\"  \r\nFROM USER_TABLES where blocks>100 and (NUM_ROWS*AVG_ROW_LEN/1024/1024/0.9)/(BLOCKS*8192/1024/1024)<0.3 \r\norder by (NUM_ROWS*AVG_ROW_LEN/1024/1024/0.9)/(BLOCKS*8192/1024/1024) desc ');
INSERT INTO `my_scripts` VALUES ('23', '索引碎片', 'Oracle', 'Monitor', 'select name,\r\n       del_lf_rows,\r\n       lf_rows,\r\n       round(del_lf_rows / decode(lf_rows, 0, 1, lf_rows) * 100, 0) || \'%\' frag_pct\r\n  from index_stats\r\n where round(del_lf_rows / decode(lf_rows, 0, 1, lf_rows) * 100, 0) > 30;\r\n');

-- ----------------------------
-- Table structure for tab_alarm_conf
-- ----------------------------
DROP TABLE IF EXISTS `tab_alarm_conf`;
CREATE TABLE `tab_alarm_conf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_type` varchar(255) DEFAULT NULL,
  `alarm_name` varchar(255) DEFAULT NULL,
  `judge` varchar(255) DEFAULT NULL,
  `jdg_value` float DEFAULT NULL,
  `jdg_des` varchar(255) DEFAULT NULL,
  `select_sql` text,
  `jdg_sql` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of tab_alarm_conf
-- ----------------------------
INSERT INTO `tab_alarm_conf` VALUES ('1', 'Oracle', 'Oracle数据库通断告警', '>=', '1', '连续中断次数', 'select count(*) from oracle_db', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库通断告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name\r\n             ) content\r\n  from oracle_db\r\n where mon_status = \'connected error\'\r\n and %s>0');
INSERT INTO `tab_alarm_conf` VALUES ('2', 'Oracle', 'Oracle数据库表空间使用率告警', '>=', '90', '使用百分比', 'select count(*) from oracle_tbs', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库表空间使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n 表空间名：\',\r\n              tbs_name,\r\n              \'\\n 表空间大小(GB)：\',\r\n              size_gb,\r\n              \'\\n 表空间使用率：\',\r\n              pct_used,\r\n              \'%%\',\r\n              \'\\n 表空间剩余大小(GB)：\',\r\n              free_gb) content\r\n  from oracle_tbs\r\n where pct_used > %s and free_gb<1');
INSERT INTO `tab_alarm_conf` VALUES ('4', 'Oracle', 'Oracle数据库临时表空间告警', '>=', '90', '使用百分比', 'select count(*) from oracle_tmp_tbs', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库临时表空间使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n 临时表空间名：\',\r\n              tmp_tbs_name,\r\n              \'\\n 临时表空间大小(MB)：\',\r\n              total_mb,\r\n              \'\\n 临时表空间使用率：\',\r\n              pct_used,\r\n              \'%%\',\r\n              \'\\n 临时表空间已使用大小(MB)：\',\r\n              used_mb) content\r\n  from oracle_tmp_tbs\r\n where pct_used > %s and total_mb-used_mb<1000');
INSERT INTO `tab_alarm_conf` VALUES ('6', 'Oracle', 'Oracle数据库Undo表空间告警', '>=', '90', '使用百分比', 'select count(*) from oracle_undo_tbs\r\n', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库undo表空间使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n undo表空间名：\',\r\n              undo_tbs_name,\r\n              \'\\n undo表空间大小(MB)：\',\r\n              total_mb,\r\n              \'\\n undo表空间使用率：\',\r\n              pct_used,\r\n              \'%%\',\r\n              \'\\n undo表空间已使用大小(MB)：\',\r\n              used_mb) content\r\n  from oracle_undo_tbs\r\n where pct_used > %s and total_mb-used_mb<1000');
INSERT INTO `tab_alarm_conf` VALUES ('8', 'Oracle', 'Oracle数据库连接数告警', '>=', '90', '使用百分比', 'select count(*) from oracle_db where current_process is not null', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库连接数使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n 最大连接数：\',\r\n              max_process,\r\n              \'\\n 当前连接数：\',\r\n              current_process,\r\n              \'\\n 连接数使用率：\',\r\n              percent_process,\r\n              \'%%\') content\r\n  from oracle_db\r\n where percent_process > %s');
INSERT INTO `tab_alarm_conf` VALUES ('9', 'Oracle', 'Oracle数据库adg延迟告警', '>=', '300', '单位：秒', 'select count(*) from oracle_db where adg_transport_lag is not null or adg_apply_lag is not null', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库ADG延迟告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n ADG延迟时间(transport)：\',\r\n              adg_transport_value,\r\n              \'(秒)\',\r\n              \'\\n ADG延迟时间(apply)：\',\r\n              adg_apply_value,\r\n              \'(秒)\') content\r\n  from oracle_db\r\n where length(adg_transport_lag)>0 and length(adg_apply_lag)>0 and\r\n least(adg_transport_value,adg_apply_value) > %s');
INSERT INTO `tab_alarm_conf` VALUES ('10', 'Oracle', 'Oracle数据库后台日志告警', '', null, '检测后台日志异常', 'select count(*) from oracle_db', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库后台日志告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \' \\n 异常信息:\',\r\n              err_info\r\n             ) content\r\n  from oracle_db\r\n where err_info is not null');
INSERT INTO `tab_alarm_conf` VALUES ('11', 'Oracle', 'Oracle数据库综合性能告警', '>=', '100', '单位时间内等待事件数量', 'select count(*) from oracle_db', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,\r\n       concat(tags,\r\n              \':Oracle数据库综合性能告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \' \\n 等待事件数量:\',\r\n              cnt_all) content\r\n  from (select tags, host, port, service_name, sum(event_cnt) cnt_all\r\n          from oracle_db_event_his\r\n         where timestampdiff(minute, chk_time, current_timestamp()) < 30\r\n         group by tags, host, port, service_name) t\r\n where cnt_all > %d ');
INSERT INTO `tab_alarm_conf` VALUES ('12', 'Oracle', 'Oracle数据库pga使用率告警', '>=', '90', '使用百分比', 'select count(*) from oracle_db where pga_used_pct is not null', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库PGA使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \' \\n PGA使用大小(MB)：\',\r\n              pga_used_size,\r\n              \'\\n PGA使用率：\',\r\n              pga_used_pct,\r\n              \'%%\') content\r\n  from oracle_db\r\n where pga_used_pct > %s');
INSERT INTO `tab_alarm_conf` VALUES ('13', 'Oracle', 'Oracle数据库归档使用率告警', '>=', '90', '使用百分比', 'select count(*) from oracle_db where archive_used is not null', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库归档使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n 归档使用率：\',\r\n              archive_used,\r\n              \'%%\') content\r\n  from oracle_db\r\n where archive_used > %s');
INSERT INTO `tab_alarm_conf` VALUES ('14', 'Oracle', 'Oracle数据库锁异常告警', '>=', '100', '锁定时间，单位：秒', 'select count(*) from oracle_lock', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库锁异常告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n 会话SID：\',\r\n              session_id,\r\n              \'\\n 等待时间：\',\r\n              ctime,\r\n              \'(秒)\',\r\n              \'\\n 锁类型：\',\r\n              type) content\r\n  from oracle_lock\r\n where session like \'Waiter%%\'\r\n and ctime > \'%s\'');
INSERT INTO `tab_alarm_conf` VALUES ('15', 'Oracle', 'Oracle数据库密码过期告警', '<=', '7', '密码过期剩余时间，单位：天', 'select count(*) from oracle_expired_pwd', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据库密码过期告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n 用户名：\',\r\n              username,\r\n              \'\\n 到期时间：\',\r\n              result_number,\r\n              \'(天)\') content\r\n  from oracle_expired_pwd');
INSERT INTO `tab_alarm_conf` VALUES ('16', 'Oracle', 'Oracle失效索引告警', null, null, '检测失效索引', 'select count(*) from oracle_invalid_index ', 'select tags,\r\n       concat(host, \':\', port, \'/\', service_name) url,  \r\n       concat(tags,\r\n              \':Oracle数据失效索引告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \'/\',\r\n              service_name,\r\n              \'\\n 用户名称：\',\r\n              owner,\r\n              \'\\n 索引名称：\',\r\n              index_name,\r\n              \'\\n 分区名称：\',\r\n              partition_name,\r\n              \'\\n 索引状态：\',\r\n              status) content\r\n  from oracle_invalid_index');
INSERT INTO `tab_alarm_conf` VALUES ('17', 'Linux', 'Linux主机通断告警', null, '1', '连续中断次数', 'select count(*) from os_info', 'select tags,\r\n       host url,  \r\n       concat(tags,\r\n              \':Linux主机通断告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 主机IP: \',\r\n              host\r\n             ) content\r\n  from os_info\r\n where mon_status = \'connected error\' and 99 > %s');
INSERT INTO `tab_alarm_conf` VALUES ('18', 'Linux', 'Linux主机CPU使用率告警', '>=', '90', '使用百分比', 'select count(*) from os_info where cpu_used is not null', 'select tags,\r\n       host url,\r\n       concat(tags,\r\n              \':Linux主机CPU使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 主机IP: \',\r\n              host,\r\n              \'\\n CPU使用率：\',\r\n              cpu_used,\r\n              \'%%\') content\r\n  from os_info\r\n where cpu_used > %s');
INSERT INTO `tab_alarm_conf` VALUES ('19', 'Linux', 'Linux主机内存使用率告警', null, '90', '使用百分比', 'select count(*) from os_info where  mem_used is not null', 'select tags,\r\n       host url,  \r\n       concat(tags,\r\n              \':Linux主机内存使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 主机IP: \',\r\n              host,\r\n              \'\\n 内存使用率：\',\r\n              mem_used,\r\n              \'%%\'\r\n             ) content\r\n  from os_info\r\n where mem_used > %s');
INSERT INTO `tab_alarm_conf` VALUES ('20', 'Linux', 'Linux主机文件系统使用率告警', '>=', '95', '使用百分比', 'select count(*) from os_filesystem', 'select tags,\r\n       host url,  \r\n       concat(tags,\r\n              \':Linux主机文件系统使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 主机IP: \',\r\n              host,\r\n              \' \\n 目录名称：\',\r\n              name,\r\n              \' \\n 目录总大小(GB)：\',\r\n              size,\r\n              \'\\n 目录可用大小(GB)\',\r\n              avail,\r\n              \'\\n 使用率：\',\r\n              pct_used,\r\n              \'%%\'\r\n             ) content\r\n  from os_filesystem\r\n where pct_used > %s\r\n       and avail < 5');
INSERT INTO `tab_alarm_conf` VALUES ('21', 'MySQL', 'MySQL数据库通断告警', '>=', '1', '连续中断次数', '\r\nselect count(*) from mysql_db', 'select tags,\r\n       concat(host, \':\', port) url,  \r\n       concat(tags,\r\n              \':MySQL数据库通断告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 数据库url: \',\r\n              host,\r\n              \':\',\r\n              port\r\n             ) content\r\n  from mysql_db\r\n where mon_status = \'connected error\' and 99 > %s');
INSERT INTO `tab_alarm_conf` VALUES ('23', 'Linux', 'Linux主机swap使用率告警', '>=', '10', '使用百分比', 'select count(*) from os_info where  swap_used is not null', 'select tags,\r\n       host url,  \r\n       concat(tags,\r\n              \':Linux主机SWAP使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n 主机IP: \',\r\n              host,\r\n              \'\\n SWAP使用率：\',\r\n              swap_used,\r\n              \'%%\'\r\n             ) content\r\n  from os_info\r\n where swap_used > %s');
INSERT INTO `tab_alarm_conf` VALUES ('24', 'Redis', 'Redis通断告警', '>=', '1', '连续中断次数', 'select count(*) from redis', 'select tags,\r\n       concat(host, \':\', port) url,  \r\n       concat(tags,\r\n              \':Redis通断告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n Redis url: \',\r\n              host,\r\n              \':\',\r\n              port\r\n             ) content\r\n  from redis\r\n where mon_status = \'connected error\' and 99 > %s');
INSERT INTO `tab_alarm_conf` VALUES ('25', 'Redis', 'Redis内存使用率告警', null, '80', '使用百分比', 'select count(*) from redis where  used_memory_pct is not null', 'select tags,\r\n       concat(host, \':\', port) url,  \r\n       concat(tags,\r\n              \':Redis内存使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n Redis url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \' \\n 最大内存配置(MB)\',\r\n              max_memory,\r\n              \' \\n 使用内存大小(MB)\',\r\n              used_memory,\r\n              \' \\n 内存使用率\',\r\n              used_memory_pct,\r\n              \'%%\'\r\n             ) content\r\n  from redis\r\n where used_memory_pct > %s');
