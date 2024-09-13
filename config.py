import os
db_username = os.getenv("costco_purchases_user")
db_password = os.getenv("costco_purchases_password")
db_host = 'localhost'
db = 'costcopurchases'

# Queries
total_household_spending_query = "SELECT TransactionDate, SoldPrice FROM TRANSACTIONS"
member_spending_query = "SELECT TransactionDate, SoldPrice, PersonID FROM TRANSACTIONS WHERE PersonID IN (1, 2, 3)"

# mappings
member_ids = {
    1: "Angel",
    2: "Andrew",
    3: "Katie"
}