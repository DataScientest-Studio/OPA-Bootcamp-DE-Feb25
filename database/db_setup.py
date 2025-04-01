import psycopg2

# load host address
with open('host.txt', 'r') as file:
    lines = file.readlines()  # Returns a list of lines
    host_name = lines[0].strip()  # remove trailing white space
#connect database
conn = psycopg2.connect(database="crypto_db",
                        host=host_name,
                        user="daniel",
                        password="datascientest",
                        port=5432)

# next create a cursor
cur = conn.cursor()

print("---------------------------------")
print("-- Create Crypto_ID table")
print("---------------------------------")
cur.execute("""CREATE TABLE IF NOT EXISTS Crypto_ID(
    Crypto_ID serial PRIMARY KEY,
    Crypto_name varchar(200) NOT NULL
);""")

print("---------------------------------")
print("-- Create Currency_ID table")
print("---------------------------------")
cur.execute("""CREATE TABLE IF NOT EXISTS Currency_ID(
    Currency_ID serial PRIMARY KEY,
    Currency_name varchar(200) NOT NULL
);""")

print("---------------------------------")
print("-- Create Interval_ID table")
print("---------------------------------")
cur.execute("""CREATE TABLE IF NOT EXISTS Interval_ID(
    Interval_ID serial PRIMARY KEY,
    Interval_name varchar(200) NOT NULL
);""")

print("---------------------------------")
print("-- Create Time_ID table")
print("---------------------------------")
cur.execute("""CREATE TABLE IF NOT EXISTS Time_ID(
    Time_ID serial PRIMARY KEY,
    Time_stamp varchar(200) NOT NULL
    
);""")

print("---------------------------------")
print("-- Create Main_Tb table")
print("---------------------------------")
cur.execute("""CREATE TABLE IF NOT EXISTS Main_Tb(
    Time_ID INTEGER REFERENCES Time_ID(Time_ID),
    Crypto_ID INTEGER REFERENCES Crypto_ID(Crypto_ID),
    Currency_ID INTEGER REFERENCES Currency_ID(Currency_ID),
    Interval_ID INTEGER REFERENCES Interval_ID(Interval_ID),
    Open_price float NOT NULL,
    Close_price float NOT NULL,
    High_price float NOT NULL,
    Low_price float NOT NULL,
    Volume float NOT NULL,
    Close_time date NOT NULL,
    Nr_trades int NOT NULL,
    Quote_asset_volume float NOT NULL,
    TB_based_asset_volume float NOT NULL,
    TB_quote_asset_volume float NOT NULL
);""")


# Commit the changes
conn.commit()