#!/usr/bin/env python3

import os
import sys
import time

sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/..'))

from naga_web_api import NagaClient

client = NagaClient()
session = client.get_session()

epoch_24_hours_before = int(time.time()) - 60

# 15 minutes resolution

for item in client.get_market_history(session, 'OIL.WTI#', epoch_24_hours_before, resolution=15):
    print(item)

# 30 minutes resolution

for item in client.get_market_history(session, 'OIL.WTI#', epoch_24_hours_before, resolution=30):
    print(item)
