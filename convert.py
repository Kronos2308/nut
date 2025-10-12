import json
import sqlite3

json_file = "titledb/titles.json"
db_file = "titles.db"

# Leer JSON completo
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Crear base de datos
conn = sqlite3.connect(db_file)
c = conn.cursor()

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

c.execute("CREATE INDEX IF NOT EXISTS idx_name ON games (name)")
c.execute("CREATE INDEX IF NOT EXISTS idx_releaseDate ON games (releaseDate)")
c.execute("CREATE INDEX IF NOT EXISTS idx_rank ON games (rank)")

count = 0
for uid, content in data.items():
    # --- FILTRO ---
    # descartar si todos los campos principales son None o vacíos
    if (
        not content.get("name")
        and not content.get("releaseDate")
        and (content.get("size") in (0, None))
        and not content.get("bannerUrl")
        and not content.get("category")
    ):
        continue  # saltar este registro

    name = content.get("name")
    release_date = content.get("releaseDate")
    rank = content.get("rank")
    size = content.get("size")
    json_str = json.dumps(content, ensure_ascii=False)

    c.execute("""
        INSERT OR REPLACE INTO games (uid, name, releaseDate, rank, size, json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (uid, name, release_date, rank, size, json_str))

    count += 1

conn.commit()
conn.close()

print(f"✅ Base de datos creada con {count} registros válidos en '{db_file}'")
