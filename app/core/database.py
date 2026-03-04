from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URI = "mongodb+srv://biku404notfound_db_user:C6dTllu1ibnepuC0@clusterstock.xwror2w.mongodb.net/?appName=ClusterStock"
DB_NAME = "test"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

stock_prices: Collection = db.stock_daily_prices
stocks_master: Collection = db.stocks_master

# Create Indexes
stock_prices.create_index(
    [("symbol", 1), ("date", 1)],
    unique=True
)

stocks_master.create_index(
    [("symbol", 1)],
    unique=True
)