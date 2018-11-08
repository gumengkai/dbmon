groupadd oinstall
groupadd dba
chattr -i /etc/passwd /etc/shadow
useradd -g oinstall -G dba  oracle
echo "oracle           soft    nproc           2047" >> /etc/security/limits.conf
echo "oracle           hard    nproc           16384"  >> /etc/security/limits.conf
echo "oracle           soft    nofile          65536"  >> /etc/security/limits.conf
echo "oracle           hard    nofile          65536"  >> /etc/security/limits.conf
echo "oracle           soft    stack           10240"  >> /etc/security/limits.conf
echo "oracle           soft    memlock         unlimited"  >> /etc/security/limits.conf
echo "oracle           hard    memlock         unlimited"  >> /etc/security/limits.conf

echo "kernel.shmall = 4294967296" >> /etc/sysctl.conf
echo "fs.aio-max-nr = 1048576" >> /etc/sysctl.conf
echo "fs.file-max = 6815744" >> /etc/sysctl.conf
echo "kernel.shmall = 2097152" >> /etc/sysctl.conf
echo "kernel.shmmax = 980221952" >> /etc/sysctl.conf
echo "kernel.shmmni = 4096" >> /etc/sysctl.conf
echo "kernel.sem = 250 32000 100 128" >> /etc/sysctl.conf
echo "net.ipv4.ip_local_port_range = 9000 65500" >> /etc/sysctl.conf
echo "net.core.rmem_default = 262144" >> /etc/sysctl.conf
echo "net.core.rmem_max = 4194304" >> /etc/sysctl.conf
echo "net.core.wmem_default = 262144" >> /etc/sysctl.conf
sysctl -p
