import sqlite3


class OrderManagerDAO:
    def __init__(self, db_file):
        self.__startOperationTableName__="bot_symbol_start_data"
        self.__orderStatusTableName__ = "order_status"
        
        """Inicializa la conexión a la base de datos."""
        self.conn = sqlite3.connect(db_file)
        #self._crear_tabla()

        """
        def _crear_tabla(self):
        '''Crea la tabla de usuarios si no existe.'''
        cursor = self.conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.__startPriceTableName__} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_price REAL
            )
        ''')
        self.conn.commit()
        """


    #activeOperations
    @property
    def activeOperations(self):
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {self.__startOperationTableName__}"  # 'mi_tabla' es el nombre de tu tabla
        cursor.execute(query)
        return cursor.fetchall()
              
    
    def execute_insert(self, table_name, fields, values):
        """
        Función de ayuda para insertar valores en la base de datos.
        
        :param table_name: Nombre de la tabla donde insertar los datos.
        :param fields: Tupla o lista de nombres de campo.
        :param values: Tupla o lista de valores a insertar.
        :return: ID de la fila insertada.
        """
        cursor = self.conn.cursor()
        placeholders = ", ".join(["?"] * len(values))
        field_names = ", ".join(fields)
        query = f"INSERT INTO {table_name} ({field_names}) VALUES ({placeholders})"
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.lastrowid
    
    def execute_select(self, table_name, fields='*', conditions=None, params=None):
        """
        Función de ayuda para recuperar valores de la base de datos.
        
        :param table_name: Nombre de la tabla de donde recuperar los datos.
        :param fields: Lista de campos a recuperar, por defecto '*'.
        :param conditions: Condiciones para la cláusula WHERE en la consulta SQL.
        :param params: Parámetros a usar en la consulta SQL.
        :return: Lista de filas que coinciden con la consulta.
        """
        cursor = self.conn.cursor()
        field_names = ", ".join(fields) if isinstance(fields, (list, tuple)) else fields

        query = f"SELECT {field_names} FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"

        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return rows


    def createNewOrder(self,id, status):
        table_name = self.__orderStatusTableName__
        fields = ("id",	"status")
        values = (id, status)
        return self.execute_insert(table_name, fields, values)

    def registerNewOperation(self, entryPrice: float, symbol: str, longOrderId, shortOrderId):
        table_name = self.__startOperationTableName__
        fields = ("entry_price", "symbol", "long_entry_order_id", "short_entry_order_id")
        values = (entryPrice, symbol, longOrderId, shortOrderId)
        return self.execute_insert(table_name, fields, values)
        
    def registerNewOperationOld(self, entryPrice:float,symbol:str,longOrderId,shortOrderId):
        cursor = self.conn.cursor()
        query = f'''
            INSERT INTO {self.__startOperationTableName__} (entry_price,symbol,long_entry_order_id,short_entry_order_id) VALUES (?,?,?,?)
        '''
        cursor.execute(query, (entryPrice,symbol,longOrderId,shortOrderId))
        self.conn.commit()
        return cursor.lastrowid

    def getBotEntryPrice(self):
        """Obtiene todos los usuarios de la base de datos."""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {self.__startOperationTableName__}')
        return cursor.fetchall()

    def __del__(self):
        """Cierra la conexión a la base de datos."""
        self.conn.close()


if __name__ == "__main__":
    # Ejemplo de uso del DAO
    dao = OrderManagerDAO('order_manager_test.db')
    
    #dao.registerNewOperation(31.5864,"test",1,2)

    botOperationsEntryPrice = dao.getBotEntryPrice()
    for operation in botOperationsEntryPrice:
        print(operation)
