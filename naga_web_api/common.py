import uuid

CANDLE_KEYS = (
    't', 'o', 'h', 'l', 'c', 'v'
)


class BrokerClient:
    API_BASE_URL = None

    @classmethod
    def get_session(cls, username=None, password=None, account_name=None):
        raise NotImplementedError

    @classmethod
    def get_auth_headers(cls, data):
        raise NotImplementedError

    @classmethod
    def get_market_history(cls, session, symbol, start, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_market_info(cls, session, symbol):
        raise NotImplementedError

    @classmethod
    def submit_order(cls, session, symbol, config):
        raise NotImplementedError

    @classmethod
    def modify_order(cls, session, order_id, stop_loss, take_profit):
        raise NotImplementedError

    @classmethod
    def close_order(cls, session, order_id):
        raise NotImplementedError

    @staticmethod
    def parse_market_history(data, resolution):
        count = len(data['t'])

        for x in CANDLE_KEYS:
            if x not in data:
                raise KeyError(f'missing candle key - {x}')

            if len(data[x]) != count:
                raise ValueError('mismatching data count')

        for idx in range(len(data['t'])):
            yield {'ts': data['t'][idx], 'open': data['o'][idx],
                   'high': data['h'][idx], 'low': data['l'][idx],
                   'close': data['c'][idx], 'volume': data['v'][idx],
                   'resolution': resolution}

    @staticmethod
    def parse_order_info(**kwargs):
        return {
            'order_id': kwargs['order_id'],
            'symbol': kwargs['symbol'],
            'order_type': kwargs['order_type'].upper(),
            'deposit': kwargs['deposit'],
            'volume': float(kwargs['volume']),
            'open_price': float(kwargs['open_price']),
            'close_price': kwargs.get('close_price', None),
            'profit': kwargs.get('profit', None),
            'limit_price': kwargs.get('limit_price', None),
            'stop_loss': kwargs.get('stop_loss', None),
            'take_profit': kwargs.get('take_profit', None),
            'fee': kwargs.get('fee', 0),
            'tax': kwargs.get('tax', 0),
            'swap_fee': kwargs.get('swap_fee', 0),
            'is_closed': kwargs['is_closed']
        }

    @staticmethod
    def parse_market_info(data):
        return {
            'symbol': data['symbol'], 'bid': data['bid'], 'ask': data['ask'],
            'margin': data['margin'], 'min_size': data['lot_min'],
            'max_size': data['lot_max'], 'size_step': data['lot_step'],
            'is_market_open': data['is_market_open'],
            'next_market_time_open': data.get('nearest_market_opening', None),
            'next_market_time_close': data.get('nearest_market_closing', None),
            'last_update': data['last_update_date']
        }

    @staticmethod
    def get_random_uuid():
        return str(uuid.uuid4()).replace('-', '')
