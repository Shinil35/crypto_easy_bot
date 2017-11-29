from time import sleep
from EasyBot import EasyBot

# Impostazioni
product = 'ETH-EUR'

# 4€ ogni 48h, causa del limite minimo di Trading
# Sarà abbassato il 4 dic 2017 a 0.001, mentre attualmente è a 0.01, circa 3,7€ al prezzo attuale

period_duration = 48 * 60 * 60  # Tempo minimo fra due transazioni, 1 giorno
period_euro_limit =  4          # Massimi euro investiti nel periodo impostato

avg_days = 7                    # Su quanti giorni calcolare la media su cui basare gli acquisti
avg_duration = 2 * 60 * 60      # Validità della media effettuata in precedenza

loop_time = 60                  # Tempo di ciclo del while, min 60

# Main
bot = EasyBot(product, period_duration, period_euro_limit, avg_days, avg_duration)

while True:
    bot.check_market_and_buy()

    if loop_time < 60:
        sleep(60)
    else:
        sleep(loop_time)