-------------------------------------------
-- Export file for user DBMON@ORCL       --
-- Created by gmk on 2018/12/4, 11:28:57 --
-------------------------------------------

set define off
spool table.log

prompt
prompt Creating table LOGMNR_CONTENTS
prompt ==============================
prompt
create table LOGMNR_CONTENTS
(
  id               NUMBER,
  scn              NUMBER,
  start_scn        NUMBER,
  commit_scn       NUMBER,
  timestamp        DATE,
  start_timestamp  DATE,
  commit_timestamp DATE,
  xidusn           NUMBER,
  xidslt           NUMBER,
  xidsqn           NUMBER,
  xid              RAW(8),
  pxidusn          NUMBER,
  pxidslt          NUMBER,
  pxidsqn          NUMBER,
  pxid             RAW(8),
  tx_name          VARCHAR2(256),
  operation        VARCHAR2(32),
  operation_code   NUMBER,
  rollback         NUMBER,
  seg_owner        VARCHAR2(32),
  seg_name         VARCHAR2(256),
  table_name       VARCHAR2(32),
  seg_type         NUMBER,
  seg_type_name    VARCHAR2(32),
  table_space      VARCHAR2(32),
  row_id           VARCHAR2(18),
  username         VARCHAR2(30),
  os_username      VARCHAR2(4000),
  machine_name     VARCHAR2(4000),
  audit_sessionid  NUMBER,
  session#         NUMBER,
  serial#          NUMBER,
  session_info     VARCHAR2(4000),
  thread#          NUMBER,
  sequence#        NUMBER,
  rbasqn           NUMBER,
  rbablk           NUMBER,
  rbabyte          NUMBER,
  ubafil           NUMBER,
  ubablk           NUMBER,
  ubarec           NUMBER,
  ubasqn           NUMBER,
  abs_file#        NUMBER,
  rel_file#        NUMBER,
  data_blk#        NUMBER,
  data_obj#        NUMBER,
  data_objv#       NUMBER,
  data_objd#       NUMBER,
  sql_redo         VARCHAR2(4000),
  sql_undo         VARCHAR2(4000),
  rs_id            VARCHAR2(32),
  ssn              NUMBER,
  csf              NUMBER,
  info             VARCHAR2(32),
  status           NUMBER,
  redo_value       NUMBER,
  undo_value       NUMBER,
  safe_resume_scn  NUMBER,
  cscn             NUMBER,
  object_id        RAW(16),
  edition_name     VARCHAR2(30),
  client_id        VARCHAR2(64)
)
;
create index IDX_LOGMNR_ID on LOGMNR_CONTENTS (ID);

prompt
prompt Creating table SNAP_SHOW
prompt ========================
prompt
create table SNAP_SHOW
(
  id           INTEGER,
  rate         VARCHAR2(32),
  sql_id       VARCHAR2(128),
  sql_exec_cnt VARCHAR2(32),
  val1         VARCHAR2(128),
  val2         VARCHAR2(128),
  val3         VARCHAR2(128),
  val4         VARCHAR2(128),
  val5         VARCHAR2(128),
  val6         VARCHAR2(128),
  val7         VARCHAR2(128),
  val8         VARCHAR2(128),
  val9         VARCHAR2(128),
  snap_type_id INTEGER
)
;

prompt
prompt Creating table SNAP_SHOW_CONFIG
prompt ===============================
prompt
create table SNAP_SHOW_CONFIG
(
  id         INTEGER not null,
  col1       VARCHAR2(32),
  col2       VARCHAR2(32),
  col3       VARCHAR2(32),
  col4       VARCHAR2(32),
  col5       VARCHAR2(32),
  col6       VARCHAR2(32),
  col7       VARCHAR2(32),
  col8       VARCHAR2(32),
  col9       VARCHAR2(32),
  col10      VARCHAR2(32),
  col11      VARCHAR2(32),
  col12      VARCHAR2(32),
  show_type  VARCHAR2(32),
  show_title VARCHAR2(128),
  inst_info  VARCHAR2(128)
)
;


spool off
