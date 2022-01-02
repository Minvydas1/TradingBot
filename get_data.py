from replit import db

date_time = db["date"]
percent = db["percent"]
euro = db["euro"]
profit = db["profit/loss"]

print("{} {}% {}€ {}".format(date_time, percent, euro, profit))