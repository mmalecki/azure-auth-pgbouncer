# Azure Auth PgBouncer
Azure Auth PgBouncer is designed to make securing connections to Azure PostgreSQL databases with Entra ID a breeze.

It was inspired by the [GCP Cloud SQL Auth Proxy](https://github.com/GoogleCloudPlatform/cloud-sql-proxy),
but instead of doing the hard work of proxying the traffic, it orchestrates PgBouncer
to do it instead by rotating an access token and updating its configuration accordingly.

## Installation

### pip

```sh
pipx install azure-auth-pgbouncer
```

## Usage

### Locally

When starting Azure Auth PgBouncer locally, you will need to start the two processes (PgBouncer and token refresher) separately.

First, fire up the token refresher:

```sh
PID_FILE=pgbouncer.pid AUTH_FILE=users.txt PGUSER=<identity-name> azure-auth-pgbouncer
```

Then, once it's fetched its first token and `users.txt` appears in the directory,
configure PgBouncer in a file named `pgbouncer.ini`:

```ini
[databases]
* = host=<azure-postgresql-database-host>

[pgbouncer]
pool_mode = session
listen_port = 5432
listen_addr = 127.0.0.1
auth_type = trust
auth_file = users.txt
pidfile = pgbouncer.pid
server_tls_sslmode = require # verify-full recommended
```

and launch it:

```sh
pgbouncer pgbouncer.ini
```

### Docker

Due to the tight integration, PgBouncer and the token refresher come bundled in
a single Docker container.

```sh
docker run -e PGUSER=<identity-name> -it ghcr.io/mmalecki/azure-auth-pgbouncer:latest
```

### On Kubernetes

#### As a sidecar

#### As a deployment/statefulset/...
