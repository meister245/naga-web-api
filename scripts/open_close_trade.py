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

# open trade
trade_config = {
    'order_type': 'BUY',
    'limit_price': 40.84,
    'size': 0.01,
    'stop_loss': None,
    'take_profit': None
}

order_id = client.submit_order(session, 'OIL.WTI#', trade_config)
print(client.get_order(session, order_id))

# modify order
time.sleep(5)

client.modify_order(session, order_id, stop_loss=40.20, take_profit=41.00)
print(client.get_order(session, order_id))

# close order
time.sleep(5)

client.close_order(session, order_id)
print(client.get_order(session, order_id))
