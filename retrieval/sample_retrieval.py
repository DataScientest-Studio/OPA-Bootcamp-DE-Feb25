from crypto_retrieval import retrieval
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

ret = retrieval()
data = ret.retrieve_hist(interval_id="1d")
print(data)
""" df_transform = pd.json_normalize(data['data'])
df_transform['date'] = pd.to_datetime(df_transform['date'])
df_transform['priceUsd'] = pd.to_numeric(df_transform['priceUsd'])
print(df_transform)
sns.set_theme(style="darkgrid")

plt.figure(figsize=(8, 6))
sns.lineplot(x="date", y="priceUsd",
             data=df_transform)
plt.title('Bitcoin Price over time')
plt.show()  """