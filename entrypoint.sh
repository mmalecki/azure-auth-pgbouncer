#!/usr/bin/env sh

. ./venv/bin/activate

export PGBOUNCER_AUTH_FILE="$PGBOUNCER_RUN_DIR/users.txt"
export PGBOUNCER_PID_FILE="$PGBOUNCER_RUN_DIR/pgbouncer.pid"

python -m azure_auth_pgbouncer &
refresher_pid=$!

echo "Token refresher running as PID $refresher_pid"

# Wait for the first refresh to succeed before starting PgBouncer
while [ ! -f "$PGBOUNCER_AUTH_FILE" ]; do
  sleep 1
done

cd $PGBOUNCER_RUN_DIR

cat > pgbouncer.ini <<-EOF
[databases]
* = host=$PGHOST

[pgbouncer]
pool_mode = session
listen_port = 5432
listen_addr = ${LISTEN_ADDRESS:-127.0.0.1}
auth_type = trust
auth_file = $PGBOUNCER_AUTH_FILE
pidfile = $PGBOUNCER_PID_FILE
server_tls_sslmode = ${PGSSLMODE:-verify-full}
$PGBOUNCER_EXTRA_OPTIONS
EOF

exec pgbouncer pgbouncer.ini
