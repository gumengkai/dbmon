cd /home/oracle/database
mkdir -p /u01/app/oracle/oradata/orcl 
dbca -silent -createDatabase -templateName $ORACLE_HOME/assistants/dbca/templates/General_Purpose.dbc -gdbname orcl -sid orcl -characterSet ZHS16GBK
