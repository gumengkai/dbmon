# unzip /tmp/oracle_install/p13390677_112040_Linux-x86-64_1of7.zip
# unzip /tmp/oracle_install/p13390677_112040_Linux-x86-64_2of7.zip
cp -r /tmp/database /home/oracle
chown -R oracle:oinstall /home/oracle/database
cp /tmp/oracle_install/db_install.rsp /home/oracle/db_install.rsp
cp /tmp/oracle_install/6_ora_install.sh /home/oracle/6_ora_install.sh
cp /tmp/oracle_install/7_ora_dbca.sh /home/oracle/7_ora_dbca.sh
chown  oracle:oinstall /home/oracle/6_ora_install.sh
chown  oracle:oinstall /home/oracle/7_ora_dbca.sh
chown  oracle:oinstall /home/oracle/db_install.rsp
