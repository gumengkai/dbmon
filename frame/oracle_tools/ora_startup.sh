su - oracle <<EOF
lsnrctl start
EOF
su - oracle <<EOF
sqlplus '/ as sysdba'
startup;
exit;
EOF
