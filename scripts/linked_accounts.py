#!/usr/bin/env python3

import os
import sys
import time
import getpass

sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/..'))

from naga_web_api import NagaClient

client = NagaClient()

user = input('Naga.com username: ')
passwd = getpass.getpass('Naga.com hashed password: ')

# get authenticated session
session = client.get_session(
    username=user,
    password=passwd,
    account_name='demo'
)

# list available broker accounts
resp = client.list_linked_accounts(session)

account_names = []

for item in resp.json().get('data', []):
    account_names.append(item['custom_name'])

print(account_names)

# switch to another account
account = input('Broker account name: ')

if account not in account_names:
    exit('invalid account')

session = client.get_session(
    username=user,
    password=passwd,
    account_name=account
)

