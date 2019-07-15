su - oracle <<EOF
sqlplus '/ as sysdba'
alter pluggable database all open;
exit;
EOF
