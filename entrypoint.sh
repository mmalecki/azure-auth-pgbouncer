#!/usr/bin/env sh

. ./venv/bin/activate

PGBOUNCER_AUTH_FILE="$PGBOUNCER_RUN_DIR/userlist.txt" \
PGBOUNCER_PID_FILE=$PGBOUNCER_RUN_DIR/pgbouncer.pid \
  python -m token_refresh &

# Wait for the first refresh to succeed before starting PgBouncer
while [ ! -f "$PGBOUNCER_RUN_DIR/userlist.txt" ]; do
  sleep 1
done

cd $PGBOUNCER_RUN_DIR

cat > pgbouncer.ini <<-EOF
[databases]
* = host=$PGHOST

[pgbouncer]
pool_mode = session
listen_port = 5432
listen_addr = 127.0.0.1
auth_type = trust
auth_file = userlist.txt
pidfile = pgbouncer.pid
server_tls_sslmode = require
EOF

exec pgbouncer pgbouncer.ini
