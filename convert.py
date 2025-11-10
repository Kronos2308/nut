import json
import sqlite3
import os
import requests
import re
from datetime import datetime
import struct
import zlib

def loadJson(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def saveJson(data,path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def Pack(titledb: dict) -> bytes:
    flag = b"\x0E"
    # Convertir dict → JSON sin escapar Unicode ni slashes
    message = json.dumps(titledb, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    
    # Comprimir (gzcompress)
    buf = zlib.compress(message, 9)
    sz = len(buf)
    
    # SessionKey de 256 bytes de ceros
    sessionKey = b"\x00" * 256
    
    # Padding igual que PHP
    pad_len = 0x10 - (sz % 0x10)
    buf += b"\x00" * pad_len
    
    # Longitud (8 bytes little endian)
    length_bytes = struct.pack("<Q", sz)
    
    # Cabecera final
    return b"TINFOIL" + flag + sessionKey + length_bytes + buf
    
def write_file(filename: str, obj: dict):
    packed = Pack(obj)
    with open(filename, "wb") as f:
        f.write(packed)
    print(f"[✔] Guardado {len(packed)} bytes en {filename}")
    
    
json_file = "titledb/titles.json"
db_file = "titles.db"

# Leer JSON completo
data = loadJson(json_file)

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
premeta = {}
premeta['titledb'] = {}
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
    
    # Meta file
    premeta['titledb'][uid] = content;
    c.execute("""
        INSERT OR REPLACE INTO games (uid, name, releaseDate, rank, size, json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (uid, name, release_date, rank, size, json_str))

    count += 1

conn.commit()
conn.close()

#saveJson(premeta,"titleasmeta.json")

write_file("titleasmeta.tfl", premeta)

print(f"✅ Base de datos creada con {count} registros válidos en '{db_file}'")
