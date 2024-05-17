import sqlite3


class OrderManagerDAO:
    def __init__(self, db_file):
        self.__startPriceTableName__="bot_start_price"
        """Inicializa la conexión a la base de datos."""
        self.conn = sqlite3.connect(db_file)
        self._crear_tabla()

    def _crear_tabla(self):
        """Crea la tabla de usuarios si no existe."""
        cursor = self.conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.__startPriceTableName__} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_price REAL
            )
        ''')
        self.conn.commit()

    def addBotEntryPrice(self, entryPrice):
        """Inserta un nuevo usuario en la base de datos."""
        cursor = self.conn.cursor()
        query = f'''
            INSERT INTO {self.__startPriceTableName__} (entry_price) VALUES (?)
        '''
        cursor.execute(query, (entryPrice,))
        self.conn.commit()
        return cursor.lastrowid

    def getBotEntryPrice(self):
        """Obtiene todos los usuarios de la base de datos."""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {self.__startPriceTableName__}')
        return cursor.fetchall()

    def __del__(self):
        """Cierra la conexión a la base de datos."""
        self.conn.close()


if __name__ == "__main__":
    # Ejemplo de uso del DAO
    dao = OrderManagerDAO('order_manager_db_test.db')
    dao.addBotEntryPrice(31.5864)
    dao.addBotEntryPrice(22)

    botOperationsEntryPrice = dao.getBotEntryPrice()
    for operation in botOperationsEntryPrice:
        print(operation)
