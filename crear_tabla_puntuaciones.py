
import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS puntuaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    fecha TEXT NOT NULL,
    puntuacion INTEGER NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ Tabla 'puntuaciones' creada o ya existente.")
