import json, sqlite3

json_file = "titles.json"
db_file = "titles.db"

# Leer JSON desde archivo
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Crear base de datos
conn = sqlite3.connect(db_file)
c = conn.cursor()

# Crear tabla con columnas útiles
c.execute("""
CREATE TABLE IF NOT EXISTS games (
    uid TEXT PRIMARY KEY,
    name TEXT,
    releaseDate TEXT,
    rank INTEGER,
    size INTEGER,
    json TEXT
)
""")

# Crear índices para mejorar búsquedas y ordenamientos
c.execute("CREATE INDEX IF NOT EXISTS idx_name ON games (name)")
c.execute("CREATE INDEX IF NOT EXISTS idx_releaseDate ON games (releaseDate)")
c.execute("CREATE INDEX IF NOT EXISTS idx_rank ON games (rank)")

# Insertar datos
for uid, content in data.items():
    name = content.get("name")
    release_date = content.get("releaseDate")
    rank = content.get("rank")
    size = content.get("size")
    json_str = json.dumps(content, ensure_ascii=False)
    
    c.execute("""
        INSERT OR REPLACE INTO games (uid, name, releaseDate, rank, size, json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (uid, name, release_date, rank, size, json_str))

conn.commit()
conn.close()

print(f"Base de datos creada con {len(data)} registros en '{db_file}'")
