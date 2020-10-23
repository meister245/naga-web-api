# naga-web-api

Unofficial python client for NAGA.com trading platform
The library implements private API calls captured from NAGA.com web interface

The private API may change at any point in time in the future, use at your own risk.

## Usage

Install from github:

`pip install git+https://github.com/meister245/naga-web-api.git`

## Market History Collection

No login is required to collect market history data,
The backend is using an implementation of tradingview for visualizing charts

Example for data collection:

`./scripts/collect_market_data.py`

## Authenticated Sessions

In order to use trading functionality and create authenticated sessions,
a login request has to be inspected in browser developer tools.

After login action on the web UI, the response will contain a password hash.
The hashed password value will always be the same.

Example API response:
https://api-v2.swipestox.com/user/login

```
{
    "user_name":"USERNAME",
    "password":"HASHED_PASSWORD_VALUE",
    "device_uuid":"e469e0f03d85gd9365d12891fa842e51",
    "g-recaptcha-response":null,
    "get_user_info":true
}
```

## Broker Accounts

Naga.com offers multiple trading accounts, where each account is a separate logical entity,
which requires an individual session to be established for each of the accounts.

By default the DEMO account is used.

Example for listing trading accounts:

`./scripts/linked_accounts.py`

## Trading

Example for opening, updating and closing trades:

`./scripts/open_close_trade.py`
