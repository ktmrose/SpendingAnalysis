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

for person_id in person_ids:
    df_person = df_spending_monthly.xs(person_id, level='PersonID')

    # Filter for food and non-food items
    df_food = df_person.loc[:, df_person.columns.get_level_values(1).isin(config.food_items)]
    df_non_food = df_person.loc[:, df_person.columns.get_level_values(1).isin(config.non_food_items)]

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 10), sharex=True)
    
    # Plot food items with a different color scheme
    color_map = plt.get_cmap('tab20')
    food_plot = df_food.plot(kind='bar', stacked=True, ax=axes[0], color=color_map.colors[:len(df_food.columns)])
    axes[0].set_title(f'{config.member_ids[person_id]} - Monthly Spending on Food')
    axes[0].set_ylabel('Dollars Spent')

    # Plot non-food items
    non_food_plot = df_non_food.plot(kind='bar', stacked=True, ax=axes[1])
    axes[1].set_title(f'{config.member_ids[person_id]} - Monthly Spending on Non-Food')
    axes[1].set_ylabel('Dollars Spent')

    # Modify legend labels for food items
    handles, labels = axes[0].get_legend_handles_labels()
    new_labels = [label.split(", ")[1].strip(")") for label in labels]
    axes[0].legend(handles, new_labels, title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Modify legend labels for non-food items
    handles, labels = axes[1].get_legend_handles_labels()
    new_labels = [label.split(", ")[1].strip(")") for label in labels]
    axes[1].legend(handles, new_labels, title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Ensure Month format from the query is used directly
    axes[1].set_xticklabels(df_person.index.get_level_values(0).strftime('%Y-%m'))

    plt.xlabel('Month')
    plt.tight_layout()

plt.show()

db.close()

