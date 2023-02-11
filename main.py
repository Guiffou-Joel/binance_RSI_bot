# importation des bibliothèques nécessaires
import datetime
from binance.client import Client
import pandas as pd
import numpy as np
import talib as ta
import time


# definissez votre API key aet secret
API_KEY = input("Entrez votre API KEY BINANCE\n")
API_SECRET = input("Entrez votre API SECRET BINANCE\n")

# Deffinissez le time Frame du programmes
tf = -1
print("Entrez le time frame en nombre de minutes")
while tf < 0:
    print("Entrez une valeur correcte")
    try:
        tf = int(input())
    except Exception as e:
        print("Valeur incorrecte, veuillez reessayer")
        tf = -1

# Définisser le nompre de période a utiliser pour le calcule du RSI
p = -1
print("Entrez le nombre de période pour le calcule du RSI")
while p < 0:
    print("Entrez une valeur correcte")
    try:
        p = int(input())
    except Exception as e:
        print("Valeur incorrecte, veuillez reessayer")
        p = -1

# Définisser la valeur minimal pour le RSi (niveau d'acaht)
min_rsi = -1
print("Entrez la valeur minimale pour le RSI (niveau d'achat)")
while min_rsi < 0:
    print("Entrez une valeur correcte")
    try:
        min_rsi = int(input())
    except Exception as e:
        print("Valeur incorrecte, veuillez reessayer")
        min_rsi = -1

# Définisser la valeur maximale pour le RSi (niveau de vente)
max_rsi = -1
print("Entrez la valeur maximale pour le RSI (niveau de vente)")
while max_rsi < 0:
    print("Entrez une valeur correcte")
    try:
        max_rsi = int(input())
    except Exception as e:
        print("Valeur incorrecte, veuillez reessayer")
        max_rsi = -1

# Définissez la quantité de crypto monaie a acheter
q = -1
print("Entrez la quantité de crypto monaie a acheter en dollar")
while q < 0:
    print("Entrez une valeur correcte")
    try:
        q = int(input())
    except Exception as e:
        print("Valeur incorrecte, veuillez reessayer")
        q = -1

# Définissez le crypto monaie a acheter et vendre
coin = input("Entrez la crypto a achater et renvendre avec le bon formalisme correspondant. EX: BTCUSDT:  ")

# Initialisation des parametres du programmes
last_quantity = 0
buy_running = False


# Définission du client Binance
# Mettez le paramettre testnet a False pour lancer le programme sur un compte réel
client = Client (API_KEY, API_SECRET, testnet=False)

# Fonction qui détermine le flitre du lot size
def check_decimals(symbol):
    info = client.get_symbol_info(symbol)
    val = info['filters'][2]['stepSize']
    decimal = 0
    is_dec = False
    for c in val:
        if is_dec is True:
            decimal += 1
        if c == '1':
            break
        if c == '.':
            is_dec = True
    return decimal

# Déclaration de la fonction d'achat
def buy_coin(price):
    global buy_running
    global q
    global last_quantity

    quantity = q / price
    
    quantity = float(round(quantity, check_decimals(coin)))
    print("Try to buy BTCBUSD for {}$ = {} BTCBUSD".format(q, quantity))
    try:
        client.order_market_buy(symbol=coin, quantity=quantity)
        buy_running = True
        last_quantity = quantity
    except Exception as e:
        print("Une erreur est survenue lors de l'achat")
        print(e)
        print("\n Le programme continue tout de meme de fonctionner")
        buy_running = False
    
# Declaration de la fonction de vente
def sell_coin(price):
    global last_quantity
    global buy_running

    last_quantity = float(round(last_quantity, check_decimals(coin)))
    print("Try to sell BTCBUSD for {} BTCBUSD = {}$".format(last_quantity, last_quantity * price))
    try:
        client.order_market_sell(symbol=coin, quantity=last_quantity)
        buy_running = False
    except Exception as e:
        print("Une erreur est survenue lors de la vente")
        print(e)
        print("\n Le programme continue tout de meme de fonctionner")

# Déterminer le prix courant de la crypto
def get_coin_price(coin):
    try:
        r = client.get_symbol_ticker(symbol=coin)
        return float(r["price"])
    except Exception as e:
        print("Impossible de récupérer le prix du bitcoin depuis le serveur binance. Retentative.....")
        print(e)
        return False;

# Récupération des données nécessaires
def get_coin_data(coin, tf, p):
    try:
        data = client.get_historical_klines(coin, str(tf)+"m", str(tf * (p * 2))+"min ago UTC")
        frame = pd.DataFrame(data)
        frame = frame.iloc[:, :5]
        frame.columns = ["Time", "Open", "High", "Low", "Close"]
        frame = frame.set_index("Time")
        frame.index = pd.to_datetime(frame.index, unit = "ms")
        frame = frame.astype(float)
        return frame
    except Exception as e:
        print("Impossible de recevoir les données")
        print(e)
        print("\nLe programme continue tout de mm de fonctionner")
        return pd.DataFrame()

# Calcul du RSI
def rsi_calculation(df):
    try:
        df["rsi"] = ta.RSI(np.array(df["Close"]), timeperiod = p)
        df.dropna(inplace = True)
        return df
    except Exception as e:
        print("Erreur lors du calcul du RSI")
        print(e)
        print("\nLe programme continue tout de mm de fonctionner")
        return pd.DataFrame()

# Mise en place de la stratégie
def main():
    while True:
        df = get_coin_data(coin, tf, p)
        if(df.empty):
            continue
        df = rsi_calculation(df)
        if(df.empty):
            continue
        rsi = df.rsi.iloc[-1]
        print(f'Current close price is: ' + str(df.Close.iloc[-1]) + f' Current RSi value is: ' + str(rsi))

        if rsi <= min_rsi and (not buy_running):
            price = get_coin_price(coin)
            if (price == False):
                continue
            buy_coin(price)
        if rsi >= max_rsi and buy_running:
            price = get_coin_price(coin)
            if (price == False):
                continue
            sell_coin(price)


# Exécution du prgramme
if __name__ == "__main__":
    print("running program...")

    now = datetime.datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("Date et Heure =", dt_string)
    ts = now.timestamp()
    now = datetime.date.fromtimestamp(ts)

    expire_date = datetime.date(2022, 8, 9)
    #if (now > expire_date):
        #print("Cette version d'essaie a expiré. Veillez vous rapprocher du développeur GUIFFOU JOEL sur 5euros.com : https://5euros.com/profil/guiffou-joel")
        ## dd/mm/YY H:M:S
        #dt_string = expire_date.strftime("%d/%m/%Y")
        #print("Date d'expiration = ", dt_string)
        #exit()
    main()