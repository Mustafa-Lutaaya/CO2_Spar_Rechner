# # sqlite3 Module interacts with SQLite Databases
# import sqlite3

# # Class to manage the overall database connection
# class CO2:
#     def __init__(self, db_path):
#         self.conn = sqlite3.connect(db_path)
#         self.cursor = self.conn.cursor() 
    
#     # Method to create a table in the database
#     def create_table(self, table_name):
#         self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} 
#                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                             Category TEXT,
#                             Name TEXT,
#                             Count INTEGER,
#                             Base_CO2 REAL)
#                             """)
#         self.conn.commit() # Saves changes to the database

    
#     # Method to retrieve data from the table by selecting all colums for each row and returning them as a list of tuples
#     def select_data(self, table_name):
#         self.cursor.execute(f"SELECT * FROM {table_name}") 
#         return self.cursor.fetchall() 
    
#     # Method to insert a new row into the specified table with the count as 0
#     def insert_data(self, table_name, category, name, base_CO2):
#         self.cursor.execute(f"""INSERT INTO {table_name} (Category, Name, Count, Base_CO2)
#                             VALUES (?,?,?,?)
#                             """, (category, name, 0, base_CO2))
#         self.conn.commit() 

#     # Method to retrieve data grouped by category
#     def get_data_by_category(self, table_name):
#         self.cursor.execute(f"SELECT Category, Name, Count, Base_CO2 FROM {table_name}")
#         rows = self.cursor.fetchall()

#         categories = {} # Dictionary to group data by category

#         # Loops through rows
#         for row in rows:
#             category, name, count, base_CO2 = row

#             # If category not already in the dictionary, appends it
#             if category not in categories:
#                 categories[category] = []
            
#             # Appends items to the catefory
#             categories[category].append({
#                 "name": name,
#                 "count": count,
#                 "base_CO2": base_CO2
#             })

#         # Converts the dictinary into a list of dictionarues containing the category & its items
#         items = [{"category": category, "items": items} for category, items in categories.items()]
#         return items
    
#     #  Method to delete all data from table
#     # def delete_all_data(self, table_name):
#     #     self.cursor.execute(f"DELETE FROM {table_name}")
#     #     self.conn.commit()

#     # # Method to drop table
#     # def drop_table(self, table_name):
#     #     self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
#     #     self.conn.commit()
    
#     # Method to close the database connection to commit any changes properly & save resources
#     def close(self):
#         self.conn.close()  