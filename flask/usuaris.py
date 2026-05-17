import sys
from web import app, bcrypt, mariadb

username = input("Nou usuari: ")
password = input("Contrasenya: ")
rol_triat = input("Rol (admin/usuari): ").strip().lower()

# Generem el hash de la contrasenya
hashed = bcrypt.generate_password_hash(password).decode('utf-8')
print("HASH GENERAT:", hashed)

def connection():
    try:
        conn = mariadb.connect(
            user="con",
            password="patata",
            host="localhost",
            port=3306,
            database="personas"
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connectant a MariaDB (persones): {e}", file=sys.stderr)
        return None
        
with app.app_context():
    conn = connection()
    
    if conn: # Ens assegurem que la connexió ha anat bé
        cursor = conn.cursor()
        
        query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, hashed, rol_triat))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Usuari '{username}' creat amb èxit a la base de dades!")
    else:
        print("No s'ha pogut crear l'usuari perquè la connexió ha fallat.")