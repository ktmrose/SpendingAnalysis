import os
db_username = os.getenv("costco_purchases_user")
db_password = os.getenv("costco_purchases_password")
db_host = 'localhost'
db = 'costcopurchases'

# Queries
total_household_spending_query = "SELECT TransactionDate, SoldPrice FROM TRANSACTIONS WHERE YEAR(TransactionDate) = 2024"
member_spending_query = "SELECT TransactionDate, SoldPrice, PersonID FROM TRANSACTIONS WHERE PersonID IN (1, 2, 3) AND YEAR(TransactionDate) = 2024"
spending_breakdown_query = "SELECT Transactions.PersonID, Items.Category, SUM(Transactions.SoldPrice) AS TotalSoldPrice, DATE_FORMAT(Transactions.TransactionDate, '%Y-%m') AS Month FROM Transactions JOIN Items ON Transactions.ItemID = Items.ItemID WHERE Transactions.TransactionDate BETWEEN DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR) AND CURRENT_DATE GROUP BY Transactions.PersonID, Items.Category, DATE_FORMAT(Transactions.TransactionDate, '%Y-%m') ORDER BY Transactions.PersonID, Month"

# mappings to individual initials
member_ids = { 
    1: "BF",
    2: "RM",
    3: "KR"
}

non_food_items = [
    "Misc",
    "Appliance",
    "Home",
    "Pharmacy/Hygiene",
    "Clothing",
    "Single Use",
    "Gift Cards",
]

food_items = [
    "Fresh Produce",
    "Pantry",
    "Condiments",
    "Dairy",
    "Beverages",
    "Prepared Food",
    "Bread",
    "Meat",
    "Snacks",
    "Specialty Foods",
    "Frozen",
]