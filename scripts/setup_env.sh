#!/bin/sh

apk update || { echo "Network configured incorrectly, exiting..."; exit 1; }
apk upgrade
apk add postgresql16 postgresql16-contrib postgresql16-openrc \
python3 py3-pip ufw doas shadow-uidmap fuse-overlayfs iptables curl git || { echo "Community repo not configured, exiting..."; exit 1; }

### POSTGRESQL SETUP ###

IP_ADDRESS=$(/sbin/ifconfig eth0 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}')
echo "
local   all             postgres                                     scram-sha-256
host    oidc_provider   oidc_admin           ${IP_ADDRESS}/32        scram-sha-256
host    oidc_provider   oidc_service         ${IP_ADDRESS}/32        scram-sha-256" > /etc/postgresql16/pg_hba.conf || { echo "PostrgreSQL not installed, exiting..."; exit 1; }
echo "
listen_addresses = '${IP_ADDRESS}'" >> /etc/postgresql16/postgresql.conf

rc-update add postgresql
rc-service postgresql start

psql -U postgres -c "ALTER SYSTEM SET password_encryption = 'scram-sha-256'"
psql -U postgres -c "ALTER SYSTEM SET log_connections = 'on'"
psql -U postgres -c "ALTER SYSTEM SET log_disconnections = 'on'"
psql -U postgres -c "ALTER SYSTEM SET log_statement = 'all'"
psql -U postgres -c "ALTER USER postgres WITH ENCRYPTED PASSWORD 'postgres'"
psql -U postgres -c "CREATE ROLE oidc_db_owner"
psql -U postgres -c "CREATE ROLE oidc_schema_owner"
psql -U postgres -c "CREATE USER oidc_admin WITH ENCRYPTED PASSWORD 'oidc_admin' IN ROLE oidc_db_owner"
psql -U postgres -c "CREATE USER oidc_service WITH ENCRYPTED PASSWORD 'oidc_service' IN ROLE oidc_db_owner"
psql -U postgres -c "CREATE DATABASE oidc_provider WITH OWNER oidc_db_owner"
psql -U postgres -c "\c oidc_provider"
psql -U postgres -c "ALTER SCHEMA public OWNER TO oidc_schema_owner"
psql -U postgres -c "GRANT oidc_schema_owner TO oidc_admin"
psql -U postgres -c "GRANT oidc_schema_owner TO oidc_service"
psql -U postgres -c "SELECT pg_reload_conf()"

### ROOTLESS DOCKER SETUP ###

adduser dockeruser
rc-update add cgroups && rc-service cgroups start

modprobe tun || { echo "tun module not found, exiting..."; exit 1; }
echo tun >>/etc/modules
echo "dockeruser:100000:65536" > /etc/subuid
echo "dockeruser:100000:65536" > /etc/subgid

modprobe nf_tables || { echo "nf_tables module not found, exiting..."; exit 1; }
echo "nf_tables" >> /etc/modules
echo "ip_tables" >> /etc/modules
modprobe ip_tables || { echo "ip_tables module not found, exiting..."; exit 1; }

su - dockeruser -c "curl -fsSL https://get.docker.com/rootless | sh"

RUNTIME_DIR="/home/dockeruser/.docker/run"

touch /etc/init.d/docker-rootless
echo "#!/sbin/openrc-run

name=$RC_SVCNAME
description=\"Docker Application Container Engine (Rootless)\"
supervisor=\"supervise-daemon\"
command=\"/home/dockeruser/bin/dockerd-rootless.sh\"
command_args=\"\"
command_user=\"dockeruser\"
supervise_daemon_args=\" -e PATH=\"/home/dockeruser/bin:/sbin:/usr/sbin:$PATH\" -e HOME=\"/home/dockeruser\" -e XDG_RUNTIME_DIR=\"/home/dockeruser/.docker/run\"\"

reload() {
    ebegin \"Reloading $RC_SVCNAME\"
    /bin/kill -s HUP \$MAINPID
    eend $?
}" > /etc/init.d/docker-rootless

chmod +x /etc/init.d/docker-rootless
rc-update add docker-rootless
rc-service docker-rootless start

touch /home/dockeruser/.profile
chown dockeruser:dockeruser /home/dockeruser/.profile
chmod 0644 /home/dockeruser/.profile
echo "export PATH=/home/dockeruser/bin:$PATH
export XDG_RUNTIME_DIR=${RUNTIME_DIR}
export dev=False
export default_redis_pass=7WGQitkQx0aSiDKOSFPjTOae9tvcppYQ7F32JWodS5XMfh01L4iAYbAocNPpbv2U" > /home/dockeruser/.profile

echo "net.ipv4.ip_unprivileged_port_start=80" >> /etc/sysctl.conf

### FIREWALL SETUP ###

ufw disable
ufw default deny incoming
ufw allow ssh
ufw allow http
ufw allow https
ufw enable