import time
import requests
from bokeh.plotting import figure, output_file, show
from bokeh.models import LinearAxis, Range1d, PrintfTickFormatter
from bokeh.io import export_png
import pandas as pd
import numpy as np

class Chart():

    def __init__(self):
        self.chart_params = {
            'title': '',
            'colors': {
                'up': 'Green',
                'down': 'Red'
            },
            'size': {
                'height': 500,
                'width': 750
            },
            'indicators': [
                {'name': 'ema', 'period': 12, 'color': '#EDFF86'},
                {'name': 'ema', 'period': 26, 'color': '#F4743B'}
                # Need ajustement in api call if period is greater
            ],
            'tickFormat': '%1.8f'
        }
        self.book_params = {
            'title': '',
            'colors': {
                'bid': 'Green',
                'ask': 'Red'
            },
            'size': {
                'height': 500,
                'width': 750
            },
            'depth': 100,
            'tickFormat': '%1.8f'
        }


    def ema(self, df, n):
        """ Add Exponential Moving Average Series to DataFrame """
        price = df['close']
        price.fillna(method='ffill', inplace=True)
        price.fillna(method='bfill', inplace=True)
        ema = pd.Series(price.ewm(span=n, min_periods=n).mean(), name='EMA_' + str(n))
        df = df.join(ema)
        return df


    def draw_chart(self, df, params):
        """ Plot chart data """
        # Computing indicators before triming data
        for i in params['indicators']:
            if i['name'] is 'ema':
                df = self.ema(df, i['period'])
        df = df.tail(48)
        p = figure(
            x_axis_type='datetime',
            plot_width=params['size']['width'],
            plot_height=self.chart_params['size']['height'],
            title=params['title']
        )
        # Visual ajustments
        p.toolbar.logo = None
        p.toolbar_location = None
        p.title.text_color = 'whitesmoke'
        p.title.text_font = 'noto'
        p.background_fill_color = '#36393e'
        p.border_fill_color = '#36393e'
        p.grid.grid_line_color = 'whitesmoke'
        p.grid.grid_line_alpha = 0.4
        p.grid.minor_grid_line_color = 'whitesmoke'
        p.grid.minor_grid_line_alpha = 0.2
        p.outline_line_color = 'whitesmoke'
        p.outline_line_alpha = 0.3
        p.y_range = Range1d(df['low'].min() * 0.995, df['high'].max() * 1.003)
        p.extra_y_ranges = {'foo': Range1d(start=-0, end=3 * df['volume'].max())}
        p.yaxis[0].formatter = PrintfTickFormatter(format=params['tickFormat'])
        # Adding second axis for volume to the plot.
        p.add_layout(LinearAxis(y_range_name='foo'), 'right')
        p.grid[0].ticker.desired_num_ticks = 10
        p.axis.major_tick_line_color = 'whitesmoke'
        p.axis.minor_tick_line_color = 'whitesmoke'
        p.axis.axis_line_color = 'whitesmoke'
        p.yaxis[1].ticker.desired_num_ticks = 5
        p.xaxis.major_label_text_font_size = '10pt'
        p.yaxis[0].major_label_text_font_size = '10pt'
        p.axis.major_label_text_color = 'whitesmoke'
        p.axis.major_label_text_font = 'noto'
        p.yaxis[1].bounds = (0, df['volume'].max())
        inc = df['close'] > df['open']
        dec = df['open'] >= df['close']
        half_day_in_ms_width = 20 * 60 * 1000
        # volumes
        p.vbar(
            df.date[inc],
            half_day_in_ms_width,
            0,
            df.volume[inc],
            fill_color='green',
            line_color='#222222',
            y_range_name='foo',
            alpha=0.4
        )
        p.vbar(
            df.date[dec],
            half_day_in_ms_width,
            0,
            df.volume[dec],
            fill_color='red',
            line_color='#222222',
            y_range_name='foo',
            alpha=0.4
        )
        # candlesticks
        p.segment(
            df['date'],
            df['high'],
            df['date'],
            df['low'],
            color='white'
        )
        p.vbar(
            df.date[inc],
            half_day_in_ms_width,
            df.open[inc],
            df.close[inc],
            fill_color='green',
            line_color='#222222'
        )
        p.vbar(
            df.date[dec],
            half_day_in_ms_width,
            df.open[dec],
            df.close[dec],
            fill_color='red',
            line_color='#222222'
        )
        for i in params['indicators']:
            if i['name'] is 'ema':
                p.line(
                    df['date'],
                    df['EMA_{}'.format(i['period'])],
                    line_dash=(4, 4),
                    color=i['color'],
                    legend='EMA {}'.format(i['period']),
                    line_width=2
                )
        p.legend.location = 'top_left'
        p.legend.label_text_font = 'noto'
        p.legend.label_text_color = 'whitesmoke'
        p.legend.background_fill_color = '#36393e'
        p.legend.background_fill_alpha = 0.7
        return p


    def chart(self, strcur):
        """ Parametrization of the chart plot """
        cur = strcur.upper()
        end = round(time.time())
        # 48 hours of data, 30 min periods
        start = end - 2 * 86400
        if cur in ('BTC', 'XBT'):
            self.chart_params['title'] = 'BITFINEX USD-BTC'
            self.chart_params['tickFormat'] = '%f'
            url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist'
            content = requests.get(url)
            data = content.json()
            df = pd.DataFrame.from_dict(data)
            df.rename(
                columns={2: 'close', 3: 'high', 4: 'low', 1: 'open', 0: 'date', 5:'volume'},
                inplace=True
            )
            # bitfinex needs reverse index
            df = df.iloc[::-1]
            df['date'] = pd.to_datetime(df['date'], unit='ms')
        else:
            self.chart_params['tickFormat'] = '%1.8f'
            url = 'https://api.bitfinex.com/v2/candles/trade:30m:t{}BTC/hist'.format(cur)
            content = requests.get(url)
            data = content.json()
            if len(data) is 0:
                self.chart_params['tickFormat'] = '%1.8f'
                url = 'https://poloniex.com/public?command=returnChartData&currencyPair=BTC_{}&start={}&end={}&period=1800'.format(
                    cur,
                    start,
                    end
                )
                content = requests.get(url)
                data = content.json()
                if ('error') in data:
                    url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=BTC-{}&tickInterval=thirtyMin&_={}'.format(
                        cur,
                        end
                    )
                    content = requests.get(url)
                    data = content.json()
                    if not data['success']:
                        return ''
                    self.chart_params['title'] = 'BITTREX BTC-{}'.format(cur)
                    df = pd.DataFrame.from_dict(data['result'])
                    df.rename(
                        columns={'C': 'close', 'H': 'high', 'L': 'low', 'O': 'open', 'T': 'date', 'V': 'volume'},
                        inplace=True)
                    df['volume'] = df['volume'] * df['close']
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.tail(80)
                else:
                    self.chart_params['title'] = 'POLONIEX BTC-{}'.format(cur)
                    df = pd.DataFrame.from_dict(data)
                    df['date'] = pd.to_datetime(df['date'], unit='s')
            else:
                self.chart_params['title'] = 'BITFINEX BTC-{}'.format(cur)
                df = pd.DataFrame.from_dict(data)
                df.rename(
                    columns={2: 'close', 3: 'high', 4: 'low', 1: 'open', 0: 'date', 5:'volume'},
                    inplace=True
                )
                # bitfinex needs reverse index
                df = df.iloc[::-1]
                df['date'] = pd.to_datetime(df['date'], unit='ms')
                df['volume'] = df['volume'] * df['close']
        p = self.draw_chart(df, self.chart_params)
        export_png(p, filename='{}_chart.png'.format(cur))
        return '{}_chart.png'.format(cur)


    def draw_book(self, df, params):
        """ Plot order book """
        asks = df['ask'].dropna()
        bids = df['bid'].dropna()
        p = figure(
            plot_width=self.book_params['size']['width'],
            plot_height=self.book_params['size']['height'],
            title='{}\t\tBid : {:1.8f} \tAsk : {:1.8f}\tSpread : {:1.8f}'.format(
                self.book_params['title'],
                bids.index[-1],
                asks.index[0],
                asks.index[0] - bids.index[-1]
            )
        )
        p.toolbar.logo = None
        p.toolbar_location = None
        p.title.text_color = 'whitesmoke'
        p.title.text_font = 'noto'
        p.background_fill_color = '#36393e'
        p.border_fill_color = '#36393e'
        p.grid.grid_line_color = 'whitesmoke'
        p.grid.grid_line_alpha = 0.4
        p.grid.minor_grid_line_color = 'whitesmoke'
        p.grid.minor_grid_line_alpha = 0.2
        p.outline_line_color = 'whitesmoke'
        p.outline_line_alpha = 0.3
        p.xaxis.formatter = PrintfTickFormatter(format=params['tickFormat'])
        p.yaxis.formatter = PrintfTickFormatter(format='%f')
        p.axis.major_tick_line_color = 'whitesmoke'
        p.axis.minor_tick_line_color = 'whitesmoke'
        p.axis.axis_line_color = 'whitesmoke'
        p.axis.major_label_text_color = 'whitesmoke'
        p.axis.major_label_text_font = 'noto'
        p.axis.major_label_text_font_size = '10pt'
        p.x_range = Range1d(bids.index.min(), asks.index.max())
        p.y_range = Range1d(0, max(bids.max(), asks.max()))
        p.patch(
            np.append(
                np.array(asks.index),
                [np.array(asks.index).max(), np.array(asks.index).min()]
            ),
            np.append(
                asks.values,
                [0, 0]
            ),
            alpha=0.7,
            line_width=2,
            color=self.book_params['colors']['ask']
        )
        p.patch(
            np.append(
                np.array(bids.index),
                [np.array(bids.index).max(), np.array(bids.index).min()]
            ),
            np.append(
                bids.values,
                [0, 0]
            ),
            alpha=0.7,
            line_width=2,
            color=self.book_params['colors']['bid'])
        return p


    def book(self, strcur):

        cur = strcur.upper()
        if cur in ('BTC', 'XBT'):
            self.book_params['title'] = 'BITFINEX USD-BTC'
            self.book_params['tickFormat'] = '%f'
            url = 'https://api.bitfinex.com/v2/book/tBTCUSD/P0/?len={}'.format(self.book_params['depth'])
            content = requests.get(url)
            data = content.json()
            df = pd.DataFrame.from_dict(data)
            df.rename(columns={0: 'price', 1: 'count', 2: 'amount'}, inplace=True)
            #df['amount'] = df['amount'] * df['price']
            df_asks = df[['price','amount']][df['amount'] < 0]
            df_asks = df_asks.abs()
            df_bids = df[['price','amount']][df['amount'] > 0]
            df_asks.rename(
                columns={'amount': 'ask'},
                inplace=True
            )
            df_bids.rename(
                columns={'amount': 'bid'},
                inplace=True
            )
        else:
            self.book_params['tickFormat'] = '%1.8f'
            url = 'https://api.bitfinex.com/v2/book/t{}BTC/P0/?len={}'.format(cur, self.book_params['depth'])
            content = requests.get(url)
            data = content.json()
            if ('error') in data:
                # reduce depth variable for a more focused visualization around center
                url = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_{}&depth={}'.format(
                    cur,
                    self.book_params['depth']
                )
                content = requests.get(url)
                data = content.json()
                if ('error') in data:
                    url = 'https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-{}&type=both&depth=100'.format(cur)
                    content = requests.get(url)
                    data = content.json()
                    if not data['success']:
                        return ''
                    self.book_params['title'] = 'BITTREX BTC-{}'.format(cur)
                    data = data['result']
                    df_asks = pd.DataFrame.from_dict(data['sell'])
                    df_asks.rename(columns={'Rate': 'price', 'Quantity': 'ask'}, inplace=True)
                    df_bids = pd.DataFrame.from_dict(data['buy'])
                    df_bids.rename(columns={'Rate': 'price', 'Quantity': 'bid'}, inplace=True)
                    # Cuz bittrex is shit
                    df_bids = df_bids.head(self.book_params['depth'])
                    df_asks = df_asks.head(self.book_params['depth'])

                else:
                    self.book_params['title'] = 'POLONIEX BTC-{}'.format(cur)
                    df_asks = pd.DataFrame.from_dict(data['asks'])
                    df_asks.rename(columns={0: 'price', 1: 'ask'}, inplace=True)
                    df_bids = pd.DataFrame.from_dict(data['bids'])
                    df_bids.rename(columns={0: 'price', 1: 'bid'}, inplace=True)
            else:
                self.book_params['title'] = 'BITFINEX BTC-{}'.format(cur)
                df = pd.DataFrame.from_dict(data)
                df.rename(columns={0: 'price', 1: 'count', 2: 'amount'}, inplace=True)
                # df['amount'] = df['amount'] * df['price']
                df_asks = df[['price','amount']][df['amount'] < 0]
                df_asks = df_asks.abs()
                df_bids = df[['price','amount']][df['amount'] > 0]
                df_asks.rename(columns={'amount': 'ask'}, inplace=True)
                df_bids.rename(columns={'amount': 'bid'}, inplace=True)

        df_asks['ask'] = df_asks['ask']*df_asks['price'].astype(float)
        df_bids['bid'] = df_bids['bid']*df_bids['price'].astype(float)
        df_asks.set_index(['price'], inplace=True)
        df_bids.set_index('price', inplace=True)
        df_asks = df_asks.cumsum()
        df_bids = df_bids.cumsum()
        df = df_asks.join(df_bids, how='outer')
        df.index = df.index.astype(float)
        p = self.draw_book(df, self.book_params)
        export_png(p, filename='{}_book.png'.format(cur))
        return '{}_book.png'.format(cur)