su - oracle <<EOF
sqlplus '/ as sysdba'
startup nomount;
alter database mount standby database;
alter database open;
alter database recover managed standby database using current logfile disconnect from session;
exit;
EOF
