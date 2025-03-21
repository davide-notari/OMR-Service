import pymysql
from config import DB_CONFIG


class Database:
    def __init__(self, password):
        try:
            print("Connessione in corso con PyMySQL...")

            usernames = ["access", "staff"]

            for username in usernames:
                try:
                    self.conn = pymysql.connect(
                        host=DB_CONFIG["host"],
                        user=username,
                        password=password,
                        database=DB_CONFIG["database"]
                    )
                    self.cursor = self.conn.cursor()
                    self.current_user = username
                    print("Connesso con successo")
                    break

                except pymysql.MySQLError:
                    continue
                
        except pymysql.MySQLError as e:
            print(f"Errore di connessione con PyMySQL: {e}")
            raise


    def get_updates(self):
        query = f"""
            SELECT version, update_url
            FROM app_updates
            ORDER BY release_date DESC
        """

        self.cursor.execute(query)
        return self.cursor.fetchone()


    def get_all(self, table_name):
        query = f"SELECT * FROM `{table_name}`"
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def get_record_by_id(self, table_name, id_column, record_id):
        query = f"SELECT * FROM `{table_name}` WHERE `{id_column}` = %s"
        self.cursor.execute(query, (record_id,))
        record_data = self.cursor.fetchone()

        field_query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = %s 
            ORDER BY ORDINAL_POSITION
        """
        self.cursor.execute(field_query, (table_name,))
        field_names = [row[0] for row in self.cursor.fetchall()]

        return record_data, field_names


    def get_table_fields(self, table_name, exclude_id_column=None):
        exclude_condition = f"AND COLUMN_NAME != '{exclude_id_column}'" if exclude_id_column else ""
        
        query = f"""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = %s {exclude_condition}
            ORDER BY ORDINAL_POSITION
        """
        
        self.cursor.execute(query, (table_name,))
        fields = self.cursor.fetchall()

        return [
            (name, data_type, self.extract_enum_values(column_type) if "enum" in data_type else None, length)
            for name, data_type, column_type, length in fields
        ]
    


    def add_record(self, table_name, record_data, id_column):
        field_names = [field[0] for field in self.get_table_fields(table_name, id_column)]
        columns = ", ".join([f"`{field}`" for field in field_names])  
        placeholders = ", ".join(["%s"] * len(field_names))

        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        values = tuple(record_data[field] for field in field_names)

        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            print(f"Record aggiunto con successo nella tabella {table_name}.")
        except pymysql.MySQLError as e:
            print(f"Errore durante l'inserimento in {table_name}: {e}")
            self.conn.rollback()



    def delete_record(self, table_name, id_column, record_id):
        try:
            sql = f"DELETE FROM `{table_name}` WHERE `{id_column}` = %s"
            self.cursor.execute(sql, (record_id,))
            self.conn.commit()
            print(f"Record eliminato con successo dalla tabella {table_name}.")
        except pymysql.MySQLError as e:
            print(f"Errore nell'eliminazione da {table_name}: {e}")
            self.conn.rollback()



    def update_record(self, table_name, id_column, record_id, updated_data):
        set_clause = ", ".join([f"`{key}` = %s" for key in updated_data.keys()])
        values = tuple(updated_data.values()) + (record_id,)

        sql = f"UPDATE `{table_name}` SET {set_clause} WHERE `{id_column}` = %s"
        
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            print(f"Record aggiornato con successo nella tabella {table_name}.")
        except pymysql.MySQLError as e:
            print(f"Errore nell'aggiornamento di {table_name}: {e}")
            self.conn.rollback()

    
    def extract_enum_values(self, column_type):
        # **Estrae i valori degli enum**
        return column_type.replace("enum(", "").replace(")", "").replace("'", "").split(",")
    

    def get_invoices(self, client_id, clienttype):
        query = f"""
            SELECT Numero_fattura
            FROM fatture 
            WHERE {clienttype} = {client_id}
            ORDER BY Data_fattura DESC
            LIMIT 1
        """

        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] if result else None
    

    def get_invoices_list(self, client_id, client_type):
        query = f"SELECT Numero_fattura, Data_fattura, Importo FROM fatture WHERE {client_type} = {client_id}"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result


    def get_current_user(self):
        return self.current_user


    def close(self):
        self.cursor.close()
        self.conn.close()
