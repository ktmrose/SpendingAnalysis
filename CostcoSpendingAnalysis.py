import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import config

# connect to database
db = mysql.connector.connect( host=config.db_host, user=config.db_username, password=config.db_password, database=config.db)

# helper functions
def process_data(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column])
    df.set_index(date_column, inplace=True)
    return df

# first, track spending over time (months vs dollars)
df_total_spending = pd.read_sql_query(config.total_household_spending_query, db)
df_total_spending = process_data(df_total_spending, "TransactionDate")
df_monthly_dollars = df_total_spending.resample('MS').sum()
df_monthly_items = df_total_spending.resample('MS').count()

# Plot dollars as a line graph
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
df_member_spending = pd.read_sql_query(config.member_spending_query, db)

df_member_spending["TransactionDate"] = pd.to_datetime(df_member_spending["TransactionDate"])
df_member_spending.set_index('TransactionDate', inplace=True)
df_member_monthly = df_member_spending.groupby([pd.Grouper(freq="MS"), 'PersonID']).sum()

# Create a new date range that includes all months
all_dates = pd.date_range(start=df_member_spending.index.min(), end=df_member_spending.index.max(), freq='MS')

# Create a MultiIndex that includes all dates for all PersonIDs
multi_index = pd.MultiIndex.from_product([all_dates, df_member_spending['PersonID'].unique()], names=['TransactionDate', 'PersonID'])

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

handles, labels = ax.get_legend_handles_labels()
labels = [config.member_ids[int(label.split(', ')[1].strip(')'))] for label in labels]
ax.legend(handles, labels, title='Member', loc='upper left')

# third, breakdown spending per individual over time
df_spending_breakdown = pd.read_sql_query(config.spending_breakdown_query, db)
df_spending_breakdown['Month'] = pd.to_datetime(df_spending_breakdown['Month'])
df_spending_breakdown.set_index('Month', inplace=True)
df_spending_monthly = df_spending_breakdown.groupby([pd.Grouper(freq='MS'), 'PersonID', 'Category']).sum().unstack('Category').fillna(0)

# Plot stacked bar graph for each PersonID
person_ids = df_spending_breakdown['PersonID'].unique()

fig, axes = plt.subplots(nrows=1, ncols=len(person_ids), figsize=(6 * len(person_ids), 10), sharex=True)

max_y = df_spending_monthly.sum(axis=1).max()

for i, person_id in enumerate(person_ids):
    df_person = df_spending_monthly.xs(person_id, level='PersonID')

    # Plot combined items
    color_map = plt.get_cmap('tab20')
    df_person.plot(kind='bar', stacked=True, ax=axes[i], color=color_map.colors[:len(df_person.columns)])
    axes[i].set_title(f'{config.member_ids[person_id]} - Monthly Spending by Category')
    axes[i].set_ylabel('Dollars Spent')
    axes[i].set_ylim(0, max_y)
    # Create a single legend
    if (i == len(person_ids) - 1):
        axes[i].legend().set_visible(True)
    else:
        axes[i].legend().set_visible(False)

#Fourth, make a table showing the top 5 spending categories for each person

plt.show()

db.close()

