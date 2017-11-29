from time import sleep
from EasyBot import EasyBot

# Impostazioni
product = 'ETH-EUR'

period_duration = 24 * 60 * 60  # Tempo minimo fra due transazioni, 1 giorno
period_euro_limit = 2  # Massimi euro investiti nel periodo impostato

avg_days = 7  # Su quanti giorni calcolare la media su cui basare gli acquisti
avg_duration = 2 * 60 * 60  # Validità della media effettuata in precedenza

# Main
bot = EasyBot(product, period_duration, period_euro_limit, avg_days, avg_duration)

while True:
    bot.check_market_and_buy()
    sleep(5)