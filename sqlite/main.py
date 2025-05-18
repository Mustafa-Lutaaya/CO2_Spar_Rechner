from sql_lite import CO2 # Imports the CO2 Connection Class
import logging # Python Logging module for event tracking & debugging
logging.basicConfig(level=logging.DEBUG) # Sets logging level to DEBUG & enables log displays

def sql_conn():
    db_path = "Berechner.db" # Sets path to connect to the Database
    logging.info("Connecting to the 'Berechner' database") # Logs an informational message
    berechner_db = CO2(db_path) # Creates an instance of the earlier imported CO2 Class
    
    # Creates table & logs activity
    table_name = "CO2_Spar"
    # berechner_db.create_table(table_name)
    # # input("Press Enter To Delete The Database")
    # # berechner_db.delete_all_data(table_name)
    # # logging.info(f"{table_name} Data Deleted Successfully")

    # # # Adds Data To The Table
    # input("Press Enter To Add First Category The Database")
    # berechner_db.insert_data(table_name,"UNTERTEILE", "Jeans", 23.5)
    # berechner_db.insert_data(table_name,"UNTERTEILE", "Hose", 25.0)
    # berechner_db.insert_data(table_name,"UNTERTEILE", "kurze Hose", 18.0)
    # berechner_db.insert_data(table_name,"UNTERTEILE", "Leggings", 12.0)
    # berechner_db.insert_data(table_name,"UNTERTEILE", "Rock", 15.5)
    # input("Press Enter To Add Next Category To The Database")
    # berechner_db.insert_data(table_name,"JACKEN", "Jacke", 20.0)
    # berechner_db.insert_data(table_name,"JACKEN", "Sweatjacke", 13.44)
    # berechner_db.insert_data(table_name,"JACKEN", "Strickjacke", 13.58)
    # berechner_db.insert_data(table_name,"JACKEN", "Mantel", 30.0)
    # berechner_db.insert_data(table_name,"JACKEN", "Blazer", 23.0)
    # berechner_db.insert_data(table_name,"JACKEN", "Regenjacke", 22.0)
    # berechner_db.insert_data(table_name,"JACKEN", "Windbreaker", 20.0)
    # input("Press Enter To Add Next Category To The Database")
    # berechner_db.insert_data(table_name,"ACCESSORIES", "Handtasche", 15.0)
    # berechner_db.insert_data(table_name,"ACCESSORIES", "Schal / Tuch", 5.0)
    # berechner_db.insert_data(table_name,"ACCESSORIES", "Mütze / Hut", 4.0)
    # berechner_db.insert_data(table_name,"ACCESSORIES", "Gürtel", 4.0)
    # berechner_db.insert_data(table_name,"ACCESSORIES", "Sonnenbrille", 5.0)
    # input("Press Enter To Add Next Category To The Database")
    # berechner_db.insert_data(table_name,"OBERTEILE", "Baumwolle T-shirt", 8.45)
    # berechner_db.insert_data(table_name,"OBERTEILE", "Sport T-shirt", 16.9)
    # berechner_db.insert_data(table_name,"OBERTEILE", "Bluse / Hemd", 10.0)
    # berechner_db.insert_data(table_name,"OBERTEILE", "Top / Tanktop", 6.0)
    # berechner_db.insert_data(table_name,"OBERTEILE", "Pullover", 10.75)
    # berechner_db.insert_data(table_name,"OBERTEILE", "Kleid", 22.0)
    # berechner_db.insert_data(table_name,"OBERTEILE", "Longsleeve", 11.0)
    # input("Press Enter To Add Last Category To The Database")
    # berechner_db.insert_data(table_name,"EINTEILER & SCHUHE", "Jumpsuit / Overall", 25.0)
    # berechner_db.insert_data(table_name,"EINTEILER & SCHUHE", "Handschuhe", 3.0)
    # berechner_db.insert_data(table_name,"EINTEILER & SCHUHE", "Sneaker", 18.5)
    # berechner_db.insert_data(table_name,"EINTEILER & SCHUHE", "Sportschuhe", 16.0)
    # berechner_db.insert_data(table_name,"EINTEILER & SCHUHE", "Lederschuhe", 20.0)

    input("Press Enter To Close The Database")
    logging.info("Closing The Database Connection") # Logs informational message
    berechner_db.close() # Closes connection to the Caritas Database 

# Boiler Plate to run the function
if __name__ == "__main__":
    sql_conn()