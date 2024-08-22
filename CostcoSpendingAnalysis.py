import os
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

db_username = os.getenv("costco_purchases_user")
db_password = os.getenv("costco_purchases_password")
# connect to database
db = mysql.connector.connect( host='localhost', user=db_username, password=db_password, database="costcopurchases")

# first, track spending over time (months vs dollars)
allSpendingQuery = "SELECT TransactionDate, SoldPrice FROM TRANSACTIONS"
df = pd.read_sql_query(allSpendingQuery, db)

df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
df.set_index('TransactionDate', inplace=True)
df_monthly_dollars = df.resample('MS').sum()
df_monthly_items = df.resample('MS').count()

# Plots dollars as a line graph
fig, ax1 = plt.subplots(figsize=(10,6))
plt.figure(1)
ax1.plot(df_monthly_dollars.index, df_monthly_dollars['SoldPrice'], marker='o', label='Total Dollars')

# Plots items as a bar graph
ax2 = ax1.twinx()
ax2.bar(df_monthly_items.index, df_monthly_items["SoldPrice"], width=20, alpha=0.3, label='Number of Items', color='g')

# sets x-axis
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
fig.autofmt_xdate()

ax1.set_title('Total Household Costco Spending')
ax1.set_xlabel('Month')
ax1.set_ylabel('Dollars')
ax2.set_ylabel('Number of Items')
ax1.grid(True)
ax1.legend(loc='upper left', bbox_to_anchor=(0,1))
ax2.legend(loc='upper left', bbox_to_anchor=(0, 0.9))

# second, track spending over time but per person
memberSpendingQuery = "SELECT TransactionDate, SoldPrice, PersonID FROM TRANSACTIONS WHERE PersonID IN (1, 2, 3)"
df_member = pd.read_sql_query(memberSpendingQuery, db)

df_member["TransactionDate"] = pd.to_datetime(df_member["TransactionDate"])
df_member.set_index('TransactionDate', inplace=True)
df_member_monthly = df_member.groupby([pd.Grouper(freq="MS"), 'PersonID']).sum()

# Create a new date range that includes all months
all_dates = pd.date_range(start=df_member.index.min(), end=df_member.index.max(), freq='MS')

# Create a MultiIndex that includes all dates for all PersonIDs
multi_index = pd.MultiIndex.from_product([all_dates, df_member['PersonID'].unique()], names=['TransactionDate', 'PersonID'])

# Reindex DataFrame
df_member_monthly = df_member_monthly.reindex(multi_index, fill_value=0)

df_member_pivot = df_member_monthly.unstack('PersonID') # each member is a column

fig, ax = plt.subplots(figsize=(10,6))
plt.figure(2)
df_member_pivot.plot(kind='line', ax=ax)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
fig.autofmt_xdate()


plt.xticks(rotation=45)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

ax.set_title('Individual Costco Spending Over Time')
ax.set_xlabel('Month')
ax.set_ylabel('Dollars')
ax.grid(True)
ax.legend(title='PersonID', loc='upper left')

plt.show()

db.close()

