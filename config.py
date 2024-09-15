import os
db_username = os.getenv("costco_purchases_user")
db_password = os.getenv("costco_purchases_password")
db_host = 'localhost'
db = 'costcopurchases'

# Queries
total_household_spending_query = "SELECT TransactionDate, SoldPrice FROM TRANSACTIONS"
member_spending_query = "SELECT TransactionDate, SoldPrice, PersonID FROM TRANSACTIONS WHERE PersonID IN (1, 2, 3)"
spending_breakdown_query = "SELECT Transactions.PersonID, Items.IsEdible, CASE WHEN Discount > 0 THEN 'On Sale' ELSE 'Full Price' END AS DiscountStatus, SUM(SoldPrice) AS TotalSpent FROM Transactions JOIN ITEMS ON Transactions.ItemID = Items.ItemID GROUP BY PersonID, IsEdible, DiscountStatus"

# mappings to individual initials
member_ids = { 
    1: "BF",
    2: "RM",
    3: "KR"
}