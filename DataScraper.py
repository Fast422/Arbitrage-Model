# %%
import requests as r, sympy as sp, json, pandas as pd, numpy as np, ccxt, pandas as pd, ast
from web3 import Web3


# %%

class DataScraper:
    def __init__(self, api_key=""):
        self.api_key = api_key
        self.defi_llamaURL = "https://coins.llama.fi"

    def getEthPrice(self):
        url = self.defi_llamaURL + "/prices/current/coingecko:ethereum"
        request = r.get(url)
        return request.json()["coins"]["coingecko:ethereum"]["price"]

    def getFastGasPrice(self):
        request = r.get("https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=" + self.api_key)
        return request.json()["result"]["FastGasPrice"]

    def getSwapPrice(self):
        gasPrice = float(self.getFastGasPrice())
        ethPrice = float(self.getEthPrice())
        gasLimit = 356190.0
        print("Gas Price: " + str(gasPrice))
        print("Eth Price: " + str(ethPrice))
        #Equation: Price of Swap = Price of Eth / 1^9 * Gas Price * Gas Limit
        swapPrice = ethPrice / 1000000000 * gasPrice * gasLimit
        print("Swap Price: " + str(swapPrice) + " USD")
        return round(swapPrice, 2)

    def getTxnPrice(self):
        gasPrice = float(self.getFastGasPrice())
        ethPrice = float(self.getEthPrice())
        gasLimit = 21000.0
        print("Gas Price: " + str(gasPrice))
        print("Eth Price: " + str(ethPrice))
        #Equation: Price of Txn = Price of Eth / 1^9 * Gas Price * Gas Limit
        txnPrice = ethPrice / 1000000000 * gasPrice * gasLimit
        print("Txn Price: " + str(txnPrice) + " USD")
        return round(txnPrice, 2)

    def getTop100Tokens(self):
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 500,
            'page': 1,
            'sparkline': False
        }

        # Make the API request
        response = r.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Convert the response to JSON
            data = response.json()
            
            # Create a DataFrame from the JSON data
            df = pd.DataFrame(data)
            
            df = df[['id', 'symbol', 'name', 'market_cap']]
            
            #print(df.head())

            return df["symbol"].to_list()
        else:
            print(f"Failed to fetch data: {response.status_code}")





# %%
class DataTransformer:
    
    def loadData(self):
        with open("top.json", "r") as file:
            data = file.read()
            data = json.loads(data)
            df = pd.DataFrame(data["data"]["pairs"])
            df["reserveUSD"] = df["reserveUSD"].astype(float)
            df["reserveUSD"] = df["reserveUSD"].round(3)
            self.df = df
            #print(df.head(10))

    def toCSV(self):
        self.df.to_csv("uniswap.csv", index = False)

    def calculateMeanAverage(self):
        mean = self.df["reserveUSD"].mean().round(3)
        return mean
    
    def filterForBinanceTokens(self, tokenList):

        for index, row in self.df.iterrows():
            symbol1 = row["token0"]["symbol"]
            symbol2 = row["token1"]["symbol"]
            if symbol1 not in tokenList or symbol2 not in tokenList:
                self.df.drop(index, inplace=True)

        self.df["symbol1"] = self.df["token0"].apply(lambda x: x["symbol"])
        self.df["symbol2"] = self.df["token1"].apply(lambda x: x["symbol"])
        self.df["token0"] = self.df["token0"].apply(lambda x: x["id"])
        self.df["token1"] = self.df["token1"].apply(lambda x: x["id"])

        return self.df

# %%
class BinanceScraper:
    def __init__(self):
        self.exchange = ccxt.binance(
            {
                "enableRateLimit": True,
                "options": {
                    "defaultType": "future"
                }
            }
        )
    
    def getTopTokensByFuturesVolume(self):
        # Fetch all tickers
        tickers = self.exchange.fetch_tickers()
        # Sort tickers by 24h volume in descending order
        sorted_tickers = sorted(tickers.items(), key=lambda x: x[1]['quoteVolume'], reverse=True)

        # Extract top 300 tickers
        top_300_tickers = sorted_tickers[:300]

        # Convert to DataFrame
        df = pd.DataFrame([{
            'Symbol': ticker[0],
            '24h Volume': ticker[1]['quoteVolume'],
            'Last Price': ticker[1]['last'],
            '24h Change': ticker[1]['percentage']
        } for ticker in top_300_tickers])

        df["Filtered Symbol"] = df["Symbol"].apply(lambda x: x.split("/")[0])

        return df
    
# binance = BinanceScraper()
# symbols = set(binance.getTopTokensByFuturesVolume()["Filtered Symbol"])
# symbols.add("WETH")
# symbols.add("WBTC")
# symbols.add("USDT")
# symbols.add("USDC")
# symbols.add("DAI")
# symbols.add("PEPE")
# print(symbols)
# print("WBTC" in symbols)


# # %%
# transformer = DataTransformer()
# transformer.loadData()
# df = transformer.filterForBinanceTokens(symbols)
# transformer.toCSV()

# # %%
# print(df.shape)
# df



