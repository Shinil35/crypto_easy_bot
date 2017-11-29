import gdax
import datetime
import os.path
import pickle
import math

from time import time
from api_keys import API_KEY, API_SECRET, API_PASSPHRASE, SANDBOX_API_KEY, SANDBOX_API_SECRET, SANDBOX_API_PASSPHRASE


class EasyBot:

    last_buy_time = 0

    last_avg_time = 0
    last_avg = -1

    buy_attempts = 0


    def __init__(self, product, period_duration, period_euro_limit, avg_days, avg_duration):
        self.product = product
        self.period_duration = period_duration
        self.period_euro_limit = period_euro_limit
        self.avg_days = avg_days
        self.avg_duration = avg_duration

        # Controllo se ho dati salvati in un file
        self.file_path = product + ".dat"

        try:
            if os.path.exists(self.file_path):
                with (open(self.file_path, "rb")) as file:
                    self.last_buy_time = pickle.load(file)
                    print("[", product, "] Last buy time loaded from file", sep='')
        except:
            print("[", product, "] Error reading saved file ", self.file_path, sep='')
            self.last_buy_time = 0

    def can_buy(self):
        # Controllo se ho già acquistato ETH in questo periodo

        time_delta = time() - self.last_buy_time

        if time_delta < self.period_duration:
            return False

        return True

    def get_current_buy_price(self):
        public_client = gdax.PublicClient()

        # Chiede al server i prezzi di acquisto attuali
        current_prices = public_client.get_product_order_book(self.product)

        ask_price = current_prices['asks'][0][0]

        return float(ask_price)

    def calculate_avg(self):

        # Utilizzo un meccanismo di cache della media settimanale
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

        last_avg = total_avg
        last_avg_time = datetime.time()

        return total_avg

    def buy_product(self, price):

        if not self.can_buy():
            return -1

        if price <= 0:
            raise RuntimeError('Cannot buy for a negative price')

        #auth_client = gdax.AuthenticatedClient(SANDBOX_API_KEY, SANDBOX_API_SECRET, SANDBOX_API_PASSPHRASE, api_url="https://api-public.sandbox.gdax.com")
        auth_client = gdax.AuthenticatedClient(API_KEY, API_SECRET, API_PASSPHRASE)

        amount = round(self.period_euro_limit / price, 8)
        price = round(price, 8)

        resp = auth_client.buy(price=price, size=amount, product_id=self.product)

        print(resp)

        if 'id' in resp:
            # Ordine piazzato con successo
            # TODO: Verificare se l'ordine verrà mai completato

            print("[", self.product, "] Buy order placed, id: ",resp['id'] ,", status: ", resp['status'], sep='')

            self.last_buy_time = time()

            try:
                with (open(self.file_path, "wb")) as file:
                    pickle.dump(self.last_buy_time, file)
            except:
                print("[", self.product, "] Error saving file", self.file_path, sep='')

            return True

        return False

    def check_market_and_buy(self):

        if not self.can_buy():
            return False

        # Controllo se il prezzo attuale è inferiore alla media degli ultimi 7 giorni

        avg = self.calculate_avg()
        cur_price = self.get_current_buy_price()

        print_avg = avg
        print_cur_price = cur_price

        format(print_avg, '.2f')
        format(print_cur_price, '.2f')

        print("[", self.product, "] ", self.avg_days, " days average price is ", print_avg, ", current buy price is ", print_cur_price, sep='')

        if cur_price < avg:

            print("[", self.product, "] Placing buy order..", sep='')

            # Compro il product

            bought = self.buy_product(cur_price)

            if bought:
                print("[", self.product, "] Bought ", self.product, sep='')
            else:
                print("[", self.product, "] Attempt to place a buy order failed", sep='')
                self.buy_attempts += 1