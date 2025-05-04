#!/usr/bin/env python

import psutil
import signal
import time
import os
from azure.identity import DefaultAzureCredential

IDENTITY_NAME = os.getenv("PGUSER")
AUTH_FILE = os.getenv("PGBOUNCER_AUTH_FILE")
PID_FILE = os.getenv("PGBOUNCER_PID_FILE")
REFRESH_INTERVAL = int(os.getenv("AZURE_TOKEN_REFRESH_INTERVAL", 15 * 60))

RESOURCE_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"

def refresh_token():
    print('Refreshing Azure database access token')

    # Use the default Azure credential (env, managed identity, Azure CLI, etc.)
    credential = DefaultAzureCredential()
    token = credential.get_token(RESOURCE_SCOPE)

    print(f"Token acquired, writing to {AUTH_FILE} as {IDENTITY_NAME}")

    with open(AUTH_FILE, mode='w') as auth:
        auth.write(f"\"{IDENTITY_NAME}\" \"{token.token}\"\n")

    if PID_FILE is not None:
        with open(PID_FILE, mode='r') as pid:
            pgbouncers = [int(pid.read().strip())]
    else:
        pgbouncers = list(item.pid for item in psutil.process_iter() if item.name() == 'pgbouncer')

    print(f"Sending SIGHUP to running pgbouncers", pgbouncers)


    for bouncer in pgbouncers:
        try:
            print(f"Sending SIGHUP to PID {bouncer}")
            os.kill(bouncer, signal.SIGHUP)
        except e:
            print(f"Unable to send signal to PID {bouncer}: {e}")

def main():
    while True:
        refresh_token()
        time.sleep(REFRESH_INTERVAL)

if __name__ == '__main__':
    main()
