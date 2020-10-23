import time
import urllib.parse

import cachetools.func
import requests

from .common import BrokerClient


class NagaClient(BrokerClient):
    API_BASE_URL = 'https://api-v2.swipestox.com'

    def __init__(self):
        self.device_uuid = self.get_random_uuid()

    @cachetools.func.ttl_cache(ttl=300)
    def get_session(self, username=None, password=None, account_name='demo'):
        session = requests.Session()
        session.headers.update({
            'accept': '*/*',
            'accept-version': '1.*',
            'authority': 'api-v2.swipestox.com',
            'platform': 'web-trader',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'origin': 'https://naga.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        })

        if isinstance(username, str) and isinstance(password, str):
            resp = self.__login(session, username, password)
            resp.raise_for_status()

            data = resp.json().get('info', {})
            auth_headers = self.get_auth_headers(data)
            session.headers.update(auth_headers)

            session = self.get_trader_session(session, account_name)

        else:
            resp = self.__login_guest(session)
            resp.raise_for_status()

            data = resp.json().get('info', {})
            auth_headers = self.get_auth_headers(data)
            session.headers.update(auth_headers)

        return session

    def get_trader_session(self, session, account_name='demo'):
        resp = self.list_linked_accounts(session)
        resp.raise_for_status()

        accounts = resp.json().get('data', {})
        accounts = {x['terminal_id']: x for x in accounts}

        terminal_id = None

        if account_name == 'demo':
            for k, v in accounts.items():
                if v['type'] == 'D':
                    terminal_id = k

        else:
            for k, v in accounts.items():
                if v['type'] == 'R' and v['custom_name'] == account_name:
                    terminal_id = k

        if terminal_id is None:
            raise ValueError(f'trading account not found - {account_name}')

        resp = self.__create_session(session, terminal_id)
        resp.raise_for_status()

        data = resp.json().get('info', {})
        auth_headers = self.get_auth_headers(data)
        session.headers.update(auth_headers)

        return session

    @staticmethod
    def get_auth_headers(data):
        return {
            'authorization': f'JWT {data["token"]}',
            'xsrf': data['xsrf']
        }

    @classmethod
    def get_market_info(cls, session, symbol):
        resp = cls.__symbol(session, symbol)
        resp.raise_for_status()

        data = resp.json().get('data', {})
        return BrokerClient.parse_market_info(data)

    @classmethod
    def get_market_history(cls, session, symbol, start, **kwargs):
        resp = cls.__tradingview_history(session, symbol, start, **kwargs)
        resp.raise_for_status()

        data = resp.json().get('data', {})

        if data.get('s', 'no_data') == 'ok':
            return cls.parse_market_history(
                data, kwargs.get('resolution', 30)
            )

        return []

    @classmethod
    def submit_order(cls, session, symbol, config):
        resp = cls.__trade_create(
            session, symbol,
            order_type=config['order_type'],
            limit_price=config['limit_price'],
            size=config['size'],
            stop_loss=config['stop_loss'],
            take_profit=config['take_profit']
        )

        resp.raise_for_status()
        data = resp.json().get('data', {})
        return data['system_order_id']

    @classmethod
    def get_order(cls, session, order_id):
        resp = cls.__order(session, order_id)
        resp.raise_for_status()

        data = resp.json().get('data', [])

        return cls.parse_order_info(
            order_id=data['platform_order_id'], symbol=data['symbol'],
            order_type=data['type'], deposit=data['margin'],
            volume=data['volume'], open_price=data['open_price'],
            profit=data['profit'], limit_price=data['limit_price'],
            stop_loss=data['stop_loss'], take_profit=data['take_profit'],
            fee=data['commission'], swap_fee=data['swap'], tax=data['taxes'],
            is_closed=data['is_closed']
        )

    @classmethod
    def modify_order(cls, session, order_id, stop_loss=None, take_profit=None):
        resp = cls.__trade_modify(
            session, order_id,
            stop_loss=stop_loss, take_profit=take_profit
        )

        resp.raise_for_status()
        return resp.json().get('data', {})

    @classmethod
    def close_order(cls, session, order_id):
        resp = cls.__trade_close(session, order_id)

        resp.raise_for_status()
        return resp.json().get('data', {})

    @classmethod
    def list_linked_accounts(cls, session):
        return session.post(
            cls.API_BASE_URL + '/broker/list_linked_accounts',
            headers={
                **session.headers,
                'referer': 'https://naga.com/login',
                'content-length': '0'
            }
        )

    def __create_session(self, session, terminal_id):
        return session.post(
            self.API_BASE_URL + '/broker/create_session',
            headers={
                **session.headers,
                'referer': 'https://naga.com/feed',
            },
            json={
                'device_uuid': self.device_uuid,
                'terminal_id': terminal_id
            }
        )

    def __login(self, session, username, password, **kwargs):
        return session.post(
            self.API_BASE_URL + '/user/login',
            headers={
                **session.headers,
                'referer': 'https://naga.com/login',
            },
            json={
                'user_name': username,
                'password': password,
                'device_uuid': kwargs.get('device_uuid', self.device_uuid),
                'g-recaptcha-response': None,
                'get_user_info': True
            }
        )

    def __login_guest(self, session, **kwargs):
        return session.post(
            self.API_BASE_URL + '/user/guest_login',
            headers={
                **session.headers,
                'referer': 'https://naga.com/login'
            },
            json={
                'device_uuid': kwargs.get('device_uuid', self.device_uuid)
            }
        )

    @classmethod
    def __symbol(cls, session, symbol):
        symbol = urllib.parse.quote(symbol)

        return session.get(
            cls.API_BASE_URL + '/broker/symbol/' + symbol,
            headers={
                **session.headers,
                'referer': f'https://naga.com/open-trade/{symbol}'
            }
        )

    @classmethod
    def __order(cls, session, order_id):
        return session.get(
            cls.API_BASE_URL + '/broker/order',
            headers={
                **session.headers,
                'referer': f'https://naga.com/trade/{order_id}',
                'accept-version': '2.*'
            },
            params={
                'platform_order_id': order_id
            }
        )

    @classmethod
    def __orders_active(cls, session):
        return session.get(
            cls.API_BASE_URL + '/broker/order/active_orders?type=active',
            headers={
                **session.headers,
                'referer': 'https://naga.com/my-trades/active'
            }
        )

    @classmethod
    def __orders_pending(cls, session):
        return session.get(
            cls.API_BASE_URL + '/broker/order/active_orders?type=pending',
            headers={
                **session.headers,
                'referer': 'https://naga.com/my-trades/pending'
            }
        )

    @classmethod
    def __orders_closed(cls, session, terminal_id, offset=0):
        return session.get(
            cls.API_BASE_URL + '/broker/order/closed',
            headers={
                **session.headers,
                'referer': 'https://naga.com/my-trades/closed'
            },
            params={
                'terminal_id': terminal_id,
                'offset': offset
            }
        )

    @classmethod
    def __trade_create(cls, session, symbol, order_type, **kwargs):
        quoted_symbol = urllib.parse.quote(symbol)

        data = {
            'symbol': symbol, 'lots': kwargs['size'], 'type': order_type.upper(),
            'price': kwargs['limit_price'], 'sl': kwargs.get('stop_loss', None), 'tp': kwargs.get('take_profit', None),
            'duration': 60, 'private': 'N', 'expiration': None
        }

        if order_type.upper() not in ('BUY', 'SELL'):
            raise ValueError(f'invalid order type - {order_type}')

        return session.post(
            cls.API_BASE_URL + '/broker/trade/create',
            headers={
                **session.headers,
                'referer': f'https://naga.com/open-trade/{quoted_symbol}?type={order_type}'
            },
            json=data
        )

    @classmethod
    def __trade_modify(cls, session, position_id, **kwargs):
        return session.post(
            cls.API_BASE_URL + '/broker/position/modify',
            headers={
                **session.headers,
                'referer': 'https://naga/my-trades/active'
            },
            json={
                'platform_position_id': str(position_id),
                'stop_loss': kwargs.get('stop_loss', None),
                'take_profit': kwargs.get('take_profit', None)
            }
        )

    @classmethod
    def __trade_close(cls, session, position_id):
        return session.post(
            cls.API_BASE_URL + '/broker/position/close',
            headers={
                **session.headers,
                'referer': 'https://naga.com/my-trades/active'
            },
            json={
                'platform_position_id': position_id
            }
        )

    @classmethod
    def __tradingview_history(cls, session, symbol, start, **kwargs):
        quoted_symbol = urllib.parse.quote(symbol)

        return session.get(
            cls.API_BASE_URL + '/trading_view/history',
            headers={
                **session.headers,
                'referer': f'https://naga.com/open-trade/{quoted_symbol}'
            },
            params={
                'symbol': symbol,
                'from': start,
                'to': kwargs.get('end', int(time.time())),
                'resolution': kwargs.get('resolution', 30)
            }
        )
