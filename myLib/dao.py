import sqlite3

# Crear una nueva conexión a la base de datos SQLite
conn = sqlite3.connect('mi_base_de_datos.db')

# Crear un objeto cursor para interactuar con la base de datos
cursor = conn.cursor()

# Crear una nueva tabla llamada "usuarios"
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    edad INTEGER
)
''')

# Insertar datos en la tabla
cursor.execute('''
INSERT INTO usuarios (nombre, edad) VALUES ('Alice', 31), ('Bob', 22), ('Charlie', 25)
''')

# Guardar (commit) los cambios
conn.commit()

# Consultar la base de datos
cursor.execute('SELECT * FROM usuarios')
rows = cursor.fetchall()

# Mostrar los resultados
for row in rows:
    print(row)

# Cerrar la conexión con la base de datos
conn.close()
