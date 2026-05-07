from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, jsonify, Response
import mariadb, os, sys, glob, time, config
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax',
) #comprovació de coquies
# Configuracio de seguretat per les bases de dades i usuaris
app.config['SECRET_KEY'] = config.FLASK_SECRET
csrf = CSRFProtect(app)
Talisman(app, content_security_policy=None)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	conn = connection()
	cursor = conn.cursor()
	cursor.execute("SELECT id, username, rol FROM users WHERE id = %s", (user_id,))
	row = cursor.fetchone()
	conn.close()

	if row:
		return User(id=row[0], username=row[1], rol=row[2])
	return None

# Rutes
carpeta = "/home/safefall/safefall/flask/static/imatges/"
os.makedirs(carpeta, exist_ok=True)

#classe user
class User(UserMixin):
	def __init__(self, id, username, rol):
		self.id = id
		self.username = username
		self.role = rol

# Connexio a la base de dades
def connection():
	try:
		conn = mariadb.connect(
			user=config.DB_USER,
			password=config.DB_PASS,
			host="localhost",
			port=3306,
			database="personas"
		)
		return conn
	except mariadb.Error as e:
		print(f"Error connectant a MariaDB (persones): {e}", file=sys.stderr)
		return None

# Funció generadora per crear el stream de vídeo MJPEG
def generate_frames(ip_cam_segura):
    latest_filepath = os.path.join(carpeta, f"latest_{ip_cam_segura}.jpg")
    
    while True:
        if os.path.exists(latest_filepath):
            try:
                # Llegim la imatge
                with open(latest_filepath, "rb") as f:
                    frame_data = f.read()
                
                # Yield empaqueta la imatge com a part d'un stream HTTP
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            except Exception as e:
                pass 
                
        # Una petita pausa per no saturar el disc/CPU (aprox. 10 FPS màxim)
        time.sleep(0.1)

#Pagines PROTEGIDES

@app.route("/")
@login_required 
def index():
	detec = []
	camera = []
	estat = []
	caida = []
	conn = connection()
	if conn:
		cursor = conn.cursor()
		cursor.execute("select * from detecions order by date DESC LIMIT 100")
		for row in cursor.fetchall():
			detec.append({
				"id": row[0],
				"date": row[1],
				"num_personas": row[2],
				"ruta_imatge": row[3],
				"ubicacion": row[4]
			})
		
		cursor.execute("select id, camera, ip, persones, ultim_heartbeat FROM cameres")
		ara = datetime.now()

		for row in cursor.fetchall():
			ultim_hb = row[4]
			estat_connexio = "Desconnectada"

			if ultim_hb:
				diferencia = (ara - ultim_hb).total_seconds()
				if diferencia <= 60:
					estat_connexio = "Connectada"

			camera.append({
				"id": row[0],
				"camera": row[1],
				"ip": row[2],
				"persones": row[3],
				"estat_connexio": estat_connexio
			})

		cursor.execute("select * from estat_camera")
		for row in cursor.fetchall():
			estat.append({
				"ip": row[0],
				"tumbat": row[1],
				"hora": row[2],
				"alerta_enviada": row[3]
			})

		cursor.execute("select * from caidas")
		for row in cursor.fetchall():
			caida.append({
				"fecha": row[0],
				"ip": row[1],
				"ruta_imatge": row[2]
			})

		conn.close()

		return render_template("index.html", detec=detec, camera=camera, estat=estat, caida=caida)

@app.route('/galeria')
@login_required
def galeria():
    # Bloqueig per rol: si no és admin, el fem fora
	if current_user.role != 'admin':
		flash('Accés denegat: Només els administradors poden veure la galeria.', 'danger')
		return redirect(url_for('index'))
		

	all_files = glob.glob(os.path.join(carpeta, "*.jpg"))

	# Estructura jeràrquica Any -> Mes -> Dia
	grouped_data = {}

	#prefix_to_remove = os.path.abspath(app.root_path) + '/static/'

	for full_path in all_files:
		# Obté el nom del fitxer (p. ex., '20251210_124318.jpg')
		filename = os.path.basename(full_path) 

		# Extreu la part de la data/hora (p. ex., '20251210_124318')
		base_name = filename.split('.')[0] 

		try:
			# Converteix la cadena a objecte datetime
			dt_obj = datetime.strptime(base_name, "%Y%m%d_%H%M%S")
		except ValueError:
		# Ignora fitxers que no segueixen el format de data
			continue

		# Rutes relatives per a Jinja
		relative_path = os.path.relpath(full_path, start=os.path.abspath(app.root_path)).replace("\\", "/")

		# Extreure components de la data
		year = dt_obj.year
		month = dt_obj.month
		day = dt_obj.day

		# 1. Agrupar per Any
		if year not in grouped_data:
			grouped_data[year] = {}

		# 2. Agrupar per Mes
		if month not in grouped_data[year]:
			grouped_data[year][month] = {}

		# 3. Agrupar per Dia
		if day not in grouped_data[year][month]:
			grouped_data[year][month][day] = []

		# Afegir la ruta de la imatge al dia corresponent, juntament amb l'hora
		grouped_data[year][month][day].append({
			"ruta_imatge": relative_path,
			"hora": dt_obj.strftime("%H:%M:%S")
		})

	# --- Ordenar les dades (Més recent primer) ---
	final_ordered_data = []

    # Ordenar anys de manera descendent
	sorted_years = sorted(grouped_data.keys(), reverse=True)

	for year in sorted_years:
		year_data = {"year": year, "months": []}
		# Ordenar mesos de manera descendent
		sorted_months = sorted(grouped_data[year].keys(), reverse=True)

		for month in sorted_months:
			month_data = {"month": month, "days": []}
			# Ordenar dies de manera descendent
			sorted_days = sorted(grouped_data[year][month].keys(), reverse=True)

			for day in sorted_days:
				full_date_str = f"{year}-{month:02d}-{day:02d}"

				day_images = sorted(grouped_data[year][month][day], 
					key=lambda x: x['hora'], 
					reverse=True)

				month_data["days"].append({
					"day": day,
					"date_str": full_date_str,
					"imatges": day_images # Llista de {ruta_imatge, hora}
				})
            
			year_data["months"].append(month_data)

		final_ordered_data.append(year_data)

    # Enviem l'estructura de dades agrupada a la plantilla
	return render_template("galeria.html", grouped_detections=final_ordered_data)

@app.route('/video_feed/<ip_cam>')
@login_required
def video_feed(ip_cam): 

	ip_cam_segura = secure_filename(ip_cam)
    # Retornem el generador amb el tipus MIME específic de vídeo MJPEG
	return Response(generate_frames(ip_cam_segura),
		mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/directe')
@login_required
def directe():
	if current_user.role != 'admin':
		flash('Accés denegat: Només els administradors poden veure la galeria.', 'danger')
		return redirect(url_for('index'))
	
	camera = []
	conn = connection()
	if conn:
		cursor = conn.cursor()
		# Seleccionem la informació de les càmeres
		cursor.execute("SELECT id, camera, ip, persones, ultim_heartbeat FROM cameres")
		ara = datetime.now()

		for row in cursor.fetchall():
			ultim_hb = row[4]
			estat_connexio = "Desconnectada"

			# Comprovem si la càmera ha enviat un senyal en l'últim minut
			if ultim_hb:
				diferencia = (ara - ultim_hb).total_seconds()
				if diferencia <= 60:
					estat_connexio = "Connectada"

			camera.append({
				"id": row[0],
				"camera": row[1],
				"ip": row[2],
				"persones": row[3],
				"estat_connexio": estat_connexio
			})
		conn.close()

	# Enviem la llista de càmeres a la nova plantilla
	return render_template("directe.html", camera=camera)

@app.route('/login', methods=['GET', 'POST'])
def login():
	login = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		conn = connection()
		cursor = conn.cursor()
		cursor.execute("SELECT id, username, password_hash, rol FROM users WHERE username = %s", (username,))
		user_data = cursor.fetchone()
		conn.close()

		if user_data and bcrypt.check_password_hash(user_data[2], password):
			# Creem l'objecte usuari amb el rol que ve de la BD
			user_obj = User(id=user_data[0], username=user_data[1], rol=user_data[3])
			login_user(user_obj)
			return redirect(url_for('index'))
		else:
			flash('Usuari o contrasenya incorrectes', 'danger')
    
	return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Has tancat la sessió correctament.', 'info')
	return redirect(url_for('login'))

@app.route('/api/dades')
@login_required
def dades():
    conn = connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Dades per a la taula de Càmeres
    cursor.execute("select * from cameres")
    cameris_raw = cursor.fetchall()

    ara = datetime.now()
    cameris = []
    sistema_actiu = True # Variable per controlar l'estat global del sistema

    for cam in cameris_raw:
        ultim_hb = cam.get('ultim_heartbeat')
        estat_connexio = "Desconnectada"

        if ultim_hb:
            diferencia = (ara - ultim_hb).total_seconds()
            if diferencia <= 60:
                estat_connexio = "Connectada"
        
        # Si hi ha alguna càmera desconnectada, el sistema passa a estar en "Alerta"
        if estat_connexio == "Desconnectada":
            sistema_actiu = False

        cam['estat_connexio'] = estat_connexio
        cameris.append(cam)

    # 2. Dades per a la taula d'Estat
    cursor.execute("select * from estat_camera")
    estats = cursor.fetchall()

    # 3. KPI: Total de Caigudes
    cursor.execute("select count(*) as total from caidas where DATE(fecha) = CURDATE()")
    resultat_caigudes = cursor.fetchone()
    total_caigudes = resultat_caigudes['total'] if resultat_caigudes else 0

    # 4. KPI: Deteccions últimes 24 hores
    cursor.execute("select sum(num_personas) as total from detecions where DATE(date) = CURDATE()")
    resultat_deteccions = cursor.fetchone()
    
    # Ens assegurem que si SQL retorna None (perquè no hi ha dades avui), posem un 0
    if resultat_deteccions and resultat_deteccions['total'] is not None:
        total_deteccions_24h = int(resultat_deteccions['total'])
    else:
        total_deteccions_24h = 0
    cursor.close()
    conn.close()

    # Determinar el text del KPI d'Estat del Sistema
    estat_sistema_text = "Actiu" if sistema_actiu else "Revisar Càmeres"

    return jsonify(
        cameris=cameris, 
        estats=estats,
        kpis={
            'total_caigudes': total_caigudes,
            'total_deteccions_24h': total_deteccions_24h,
            'estat_sistema': estat_sistema_text
        }
    )

#api per gràfiques
@app.route('/api/estadistiques/caigudes_per_dia')
@login_required
def estadistiques_caigudes_linia():
	periode = request.args.get('periode', 'setmana')
	ara = datetime.now()

	conn = connection()
	cursor = conn.cursor()

	labels = []
	data = []

	if periode == 'dia':
		# --- LÒGICA PER A LES ÚLTIMES 24 HORES (AGRUPAT PER HORA) ---
		
		# Diccionari amb les últimes 24 hores plenes de 0s
		dades_dict = {}
		for i in range(24, -1, -1):
			hora_calc = ara - timedelta(hours=i)
			clau_hora = hora_calc.strftime('%Y-%m-%d %H')
			label_visual = hora_calc.strftime('%H:00')
			
			labels.append(label_visual)
			dades_dict[clau_hora] = 0

		# 2. Consulta SQL agrupant per hora
		query = """
			SELECT DATE_FORMAT(fecha, '%Y-%m-%d %H') as hora, COUNT(*) as total
			FROM caidas
			WHERE fecha >= NOW() - INTERVAL 24 HOUR
			GROUP BY DATE_FORMAT(fecha, '%Y-%m-%d %H')
		"""
		cursor.execute(query)
		for fila in cursor.fetchall():
			hora_db = str(fila[0])
			if hora_db in dades_dict:
				dades_dict[hora_db] = fila[1]

		
		data = list(dades_dict.values()) # Passem els valors del diccionari a la llista de dades

	else:
		# --- LÒGICA PER A SETMANA I MES (AGRUPAT PER DIES) ---
		if periode == 'mes':
			dies_enrere = 30
		else:
			dies_enrere = 7

		data_inici = ara - timedelta(days=dies_enrere)
		
		# 1. Preparem els dies amb 0s
		dades_dict = {}
		for i in range(dies_enrere + 1):
			dia_actual = (data_inici + timedelta(days=i)).date()
			labels.append(str(dia_actual))
			dades_dict[str(dia_actual)] = 0

		# 2. Consulta SQL agrupant per dia
			query = """
				SELECT DATE(fecha) as dia, count(*) as total_caigudes
				FROM caidas
				WHERE fecha >= NOW() - INTERVAL %s DAY
				GROUP BY DATE(fecha)
			"""
			cursor.execute(query, (dies_enrere,))
	for fila in cursor.fetchall():
            dia_db = str(fila[0])
            if dia_db in dades_dict:
                dades_dict[dia_db] = fila[1]
    
	data = list(dades_dict.values())

	cursor.close()
	conn.close()

	# Retornem les llistes al JavaScript. El Chart.js les pintarà sense queixar-se!
	return jsonify({'labels': labels, 'data': data})

@app.route('/api/estadistiques/caigudes_per_camera')
@login_required
def estadistiques_caigudes():
	conn = connection()
	cursor = conn.cursor()

	query = """
		select ip, count(*) as total_caigudes
		from caidas
		group by ip
		order by total_caigudes desc
	"""

	cursor.execute(query)
	resultats = cursor.fetchall()

	cursor.close()
	conn.close()

	ips_cameres = [str(fila[0]) for fila in resultats]
	totals = [fila[1] for fila in resultats]

	return jsonify({'labels': ips_cameres, 'data': totals})

# Inici de l'app
if __name__ == "__main__":
    print("Iniciant servidor web...")
    app.run(debug=False, host="0.0.0.0", port=5000, ssl_context=('certs/cert.pem', 'certs/key.pem'))
#desactivar el debug 