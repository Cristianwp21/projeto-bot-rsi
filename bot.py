from binance.client import Client
import pandas as pd
import numpy as np
import time
from telegram import Bot

# Configurações da API da Binance
API_KEY = "WGppsqHCM893qJD9IeAx20SzEw5Ewdb1IzUBzS0r9gHZRiAP8LPbtK3l1RWqwQKZ"
API_SECRET = "QrPiz5LYJS20oRJZb3JX7W5Ts7Bd7WrZ36PlG389JaHrfxHv0Th0Jd0uTZd345cB"

client = Client(API_KEY, API_SECRET)

# Configurações de mercado
SYMBOL = "BTCUSDT"  # Par de negociação
INTERVAL = Client.KLINE_INTERVAL_15MINUTE  # Intervalo de 15 minutos

# Configurações do Telegram
TELEGRAM_TOKEN = "7676787815:AAHLOCqbmuQgJN8NDgxvsgnyoH_nMhWCbyM"
CHAT_ID = "SEU_CHAT_ID_AQUI"

# Função para enviar alertas no Telegram
def enviar_alerta(mensagem):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=mensagem)

# Função para calcular o RSI
def calculate_rsi(data, period=14):
    close_prices = pd.Series([float(kline[4]) for kline in data])
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0).tolist()

# Função para buscar dados de mercado
def get_market_data(symbol, interval, limit=100):
    return client.get_klines(symbol=symbol, interval=interval, limit=limit)

# Função para verificar divergências
def verificar_divergencias(data, rsi, lookback_right=100, lookback_left=8):
    close_prices = [float(kline[4]) for kline in data]
    lows = [float(kline[3]) for kline in data]
    highs = [float(kline[2]) for kline in data]

    # Bullish Divergence
    for i in range(lookback_right, len(rsi)):
        if i - lookback_left < 0:
            continue
        rsi_hl = rsi[i] > rsi[i - lookback_right]
        price_ll = lows[i] < lows[i - lookback_right]
        if rsi_hl and price_ll:
            return "Bullish Divergence Detected!"

    # Bearish Divergence
    for i in range(lookback_right, len(rsi)):
        if i - lookback_left < 0:
            continue
        rsi_lh = rsi[i] < rsi[i - lookback_right]
        price_hh = highs[i] > highs[i - lookback_right]
        if rsi_lh and price_hh:
            return "Bearish Divergence Detected!"

    return None

# Função principal do bot
def run_bot():
    while True:
        try:
            # Busca os dados de mercado
            market_data = get_market_data(SYMBOL, INTERVAL)
            rsi = calculate_rsi(market_data)

            # Verifica divergências
            alerta = verificar_divergencias(market_data, rsi)
            if alerta:
                enviar_alerta(alerta)
                print(alerta)

            # Pausa antes da próxima verificação
            time.sleep(60)
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()
