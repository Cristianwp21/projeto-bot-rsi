from binance.client import Client
import pandas as pd
import requests
import time

# Configurações da API da Binance
API_KEY = "WGppsqHCM893qJD9IeAx20SzEw5Ewdb1IzUBzS0r9gHZRiAP8LPbtK3l1RWqwQKZ"
API_SECRET = "QrPiz5LYJS20oRJZb3JX7W5Ts7Bd7WrZ36PlG389JaHrfxHv0Th0Jd0uTZd345cB"

client = Client(API_KEY, API_SECRET)

# Configurações de mercado
SYMBOL = "BTCUSDT"  # Par de negociação
INTERVAL = Client.KLINE_INTERVAL_15MINUTE  # Intervalo de 15 minutos

# Função para calcular o RSI
def calculate_rsi(data, period=14):
    close_prices = pd.Series([float(kline[4]) for kline in data])  # Preços de fechamento
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0).tolist()  # Retorna o RSI como lista

# Função para buscar dados de mercado
def get_market_data(symbol, interval, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    return klines

# Função principal do bot
def run_bot():
    while True:
        try:
            # Busca os dados de mercado
            market_data = get_market_data(SYMBOL, INTERVAL)
            rsi = calculate_rsi(market_data)

            # Exemplo de análise: RSI abaixo de 30 (sobrevendido)
            if rsi[-1] < 30:
                print(f"Alerta: RSI em {SYMBOL} está sobrevendido ({rsi[-1]:.2f})")

            # Pausa antes da próxima verificação
            time.sleep(60)  # Aguarda 1 minuto
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente

if __name__ == "__main__":
    run_bot()