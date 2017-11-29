import gdax
import datetime

from time import time


class EasyBot:

    last_buy_time = 0

    last_avg_time = 0
    last_avg = -1

    def __init__(self, product, period_duration, period_euro_limit, avg_days, avg_duration):
        self.product = product
        self.period_duration = period_duration
        self.period_euro_limit = period_euro_limit
        self.avg_days = avg_days
        self.avg_duration = avg_duration

    def can_buy(self):
        # Controllo se ho già acquistato ETH in questo periodo

        time_delta = time() - self.last_buy_time

        if time_delta < self.period_duration:
            return False

        return True

    def get_current_buy_price(self):
        public_client = gdax.PublicClient()

        # Chiede al server i prezzi di acquisto/vendita attuali
        current_prices = public_client.get_product_order_book(self.product)

        ask_price = current_prices['asks'][0][0]

        return ask_price

    def calculate_avg(self):

        if self.last_avg != -1 and self.last_avg_time > time() - self.avg_duration:
            return self.last_avg

        public_client = gdax.PublicClient()

        # Media a blocchi di 2 ore, per i 'avg_days' giorni passati
        stop_time = datetime.datetime.utcnow()
        start_time = stop_time - datetime.timedelta(days=self.avg_days)

        # Chiede i dati al server
        history = public_client.get_product_historic_rates(self.product, start_time.isoformat(), stop_time.isoformat(),
                                                           granularity=7200)

        # Calcola la media in questi ultimi 'avg_days' giorni
        total_avg = 0
        total_count = 0

        for element in history:
            this_avg = (element[2] + element[3]) / 2
            total_avg += this_avg
            total_count += 1

        if total_count <= 0:
            raise RuntimeError('Invalid data received from the server')

        total_avg = total_avg / total_count

        print("Average price is", total_avg, self.product)

        last_avg = total_avg
        last_avg_time = datetime.time()

        return total_avg

    def buy_product(self, price):

        if not self.can_buy():
            return False

        if price <= 0:
            raise RuntimeError('Cannot buy for a negative price')

        # TODO: Buy product

        return True

    def check_market_and_buy(self):

        pass