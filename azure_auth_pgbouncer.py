#!/usr/bin/env python

import signal
import time
import os
import sys
from azure.identity import DefaultAzureCredential

IDENTITY_NAME = os.getenv("PGUSER")
AUTH_FILE = os.getenv("PGBOUNCER_AUTH_FILE", "users.txt")
PID_FILE = os.getenv("PGBOUNCER_PID_FILE", "pgbouncer.pid")
REFRESH_INTERVAL = int(os.getenv("AZURE_TOKEN_REFRESH_INTERVAL", 15 * 60))

RESOURCE_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"

if IDENTITY_NAME is None:
    print("PGUSER needs to be specified")
    sys.exit(1)

def refresh_token():
    print('Refreshing Azure database access token')

    # Use the default Azure credential (env, managed identity, Azure CLI, etc.)
    credential = DefaultAzureCredential()
    token = credential.get_token(RESOURCE_SCOPE)

    print(f"Token acquired, writing to {AUTH_FILE} as {IDENTITY_NAME}")

    with open(AUTH_FILE, mode='w') as auth:
        auth.write(f"\"{IDENTITY_NAME}\" \"{token.token}\"\n")

    if PID_FILE is not None:
        try:
            with open(PID_FILE, mode='r') as pid:
                bouncer = int(pid.read().strip())
        except Exception as e:
            print(f"Unable to open PID file, not sending SIGHUP: {e}")
            return

        try:
            print(f"Sending SIGHUP to PID {bouncer}")
            os.kill(bouncer, signal.SIGHUP)
        except Exception as e:
            print(f"Unable to send SIGHUP to PID {bouncer}: {e}")

def main():
    while True:
        refresh_token()
        time.sleep(REFRESH_INTERVAL)

if __name__ == '__main__':
    main()
