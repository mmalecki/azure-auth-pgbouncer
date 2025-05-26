# Azure Auth PgBouncer
Azure Auth PgBouncer is designed to make securing connections to Azure PostgreSQL databases with Entra ID a breeze.

It was inspired by the [GCP Cloud SQL Auth Proxy](https://github.com/GoogleCloudPlatform/cloud-sql-proxy),
but instead of doing the hard work of proxying the traffic, it orchestrates PgBouncer
to do it instead by rotating an access token and updating its configuration accordingly.

## Installation

### pipx

```sh
pipx install azure-auth-pgbouncer
```

### Docker
```sh
docker pull ghcr.io/mmalecki/azure-auth-pgbouncer:latest
```

## Usage

### Locally

When starting Azure Auth PgBouncer locally, you will need to start the two processes (PgBouncer and token refresher) separately.

First, fire up the token refresher:

```sh
PID_FILE=pgbouncer.pid AUTH_FILE=users.txt PGUSER=<identity-name> azure-auth-pgbouncer
```

Then, once it's fetched its first token and `users.txt` appears in the directory,
configure PgBouncer in a file named `pgbouncer.ini`, for example:

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
server_tls_sslmode = verify-full
```

and launch it:

```sh
pgbouncer pgbouncer.ini
```

Please note that the database host needs to be accessible over network - this
project only handles authentication, not network traversals. However,
with `server_tls_sslmode` set to `require` (as opposed to `verify-full`),
you should see no issues connecting to a proxy set up by, say, `kubectl port-forward`.

Additionally, PgBouncer limits the maximum password length to 2048 characters.
The Azure CLI credential can be longer than that. In this case, you can expect to see
the following error in PgBouncer logs:

```
ERROR password too long in auth file
```

With cloud use being the primary focus of this project, fixing this issue hasn't been
a priority.

### Docker

Due to the tight integration, PgBouncer and the token refresher come bundled in
a single Docker container.

```sh
docker run -e PGHOST=<azure-postgresql-database-host> -e PGUSER=<identity-name> -it ghcr.io/mmalecki/azure-auth-pgbouncer:latest
```

No additional configuration is needed - the `pgbouncer.ini` file is generated
by container's entrypoint.

### On Kubernetes

#### As a sidecar

Add the following init container to your deployment/statefulset/...:

```yaml
      initContainers:
        - name: azure-auth-pgbouncer
          image: ghcr.io/mmalecki/azure-auth-pgbouncer:v0.1.1
          imagePullPolicy: IfNotPresent
          restartPolicy: Always
          ports:
          - containerPort: 5432
            protocol: TCP
          env:
          - name: PGHOST
            value: <azure-postgresql-database-host>
          - name: PGUSER
            value: <identity-name>
```

#### As a deployment/statefulset/...

This method creates an unauthenticated PostgreSQL endpoint in your cluster,
where only method of checking identity used is verifying the username.
This may be fine for your use case, but you've been warned either way.
