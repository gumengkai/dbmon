echo "*           soft    nproc           65535" >> /etc/security/limits.conf
echo "*           hard    nproc           65535"  >> /etc/security/limits.conf
echo "*           soft    nofile          65535"  >> /etc/security/limits.conf
echo "*           hard    nofile          65535"  >> /etc/security/limits.conf

echo "fs.file-max = 65535" >> /etc/sysctl.conf


