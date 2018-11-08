su - oracle <<EOF
lsnrctl stop
EOF
ps -ef|grep LOCAL=NO|awk {'print $2'}|xargs kill -9
su - oracle <<EOF
sqlplus '/ as sysdba'
shutdown abort;
exit;
EOF
