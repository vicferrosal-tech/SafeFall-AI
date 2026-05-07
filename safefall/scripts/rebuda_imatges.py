from flask import Flask, request
import os, cv2, mariadb, traceback, ssl, json
from datetime import datetime as dt
import paho.mqtt.client as mqtt
import config

# importar ultralytics (YOLOv8). Si falla, dona fallback.
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as e:
    print("Ultralytics no disponible:", e)
    YOLO_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 #prevenció de fitxers massa grans
#constant de la carpeta
UPLOAD_FOLDER = '/home/safefall/safefall/flask/static/imatges/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuracions
YOLO_MODEL_NAME = "yolov8s-pose.pt"   # model "nano" per CPU
IMG_SIZE = 640                        # resolució d'entrada (adaptable)
CONF_THRESH = 0.2                     # confiança mínima detecció
LYING_TIME_SECONDS = 40               # temps per considerar caiguda prolongada
KP_Y_DIFF_RATIO = 0.20                # llindar (fracció de l'alçada del bbox) per considerar "horitzontal"

# === Connexió BBDD ===
def connection():
    return mariadb.connect(
        user=config.DB_USER,
        password=config.DB_PASS,
        host="localhost",
        port=3306,
        database="personas"
    )

# === Inicialitzar model YOLO (si està disponible) ===
pose_model = None
if YOLO_AVAILABLE:
    try:
        pose_model = YOLO(YOLO_MODEL_NAME)
        # Forcem device CPU
        try:
            pose_model.to('cpu')
        except Exception:
            pass
    except Exception as e:
        print("Error carregant model YOLO:", e)
        pose_model = None
        YOLO_AVAILABLE = False

#Funció per llegir imatge i rotar
def load_image(filepath):
    frame = cv2.imread(filepath)
    try:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    except Exception:
        pass
    return frame

# 1. LA FUNCIÓ QUE ENVIA L'MQTT
def enviar_alerta_mqtt(ip_cam, resolta=False):
    broker = "localhost"
    port = 1883
    tema = "safefall/alertes"

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    client.tls_set_context(context)

    try:
        client.connect(broker, port)
        hora_actual = dt.now().strftime("%d-%m-%Y %H:%M:%S")

        if resolta:
            tipus_alerta = "RESOLTA"
            missatge_text = f"S'ha resolt l'alerta. La persona s'ha aixecat (IP: {ip_cam})"
        else:
            tipus_alerta = "CRÍTICA"
            missatge_text = f"S'ha detectat una persona a terra (IP: {ip_cam})"

        dades_alerta = {
            "alerta": tipus_alerta,
            "ip": ip_cam,
            "hora": hora_actual,
            "missatge": missatge_text
        }

        missatge_json = json.dumps(dades_alerta, ensure_ascii=False)
        
        informacio_enviament = client.publish(tema, missatge_json, qos=1)
        informacio_enviament.wait_for_publish() 
        
        client.disconnect()
        print(f"MQTT enviat: {tipus_alerta} (Càmera: {ip_cam})")

    except Exception as e:
        print(f"Error enviant avís MQTT: {e}")

#Funció per detectar persones i obtenir keypoints amb YOLO Pose
def detect_persons_and_keypoints(frame):
    detections = []
    if frame is None:
        return detections

    if not YOLO_AVAILABLE or pose_model is None:
        # Retornem buit: la resta del sistema continuarà funcionant amb 0 persones.
        return detections

    try:
        # Executar predicció (forcem device cpu i imgsz)
        results = pose_model(frame, device='cpu', imgsz=IMG_SIZE, conf=CONF_THRESH, verbose=False)

        if len(results) == 0:
            return detections

        res = results[0] 
        # Extraiem caixes i keypoints; fem-ho robust per a diferents versions de la llibreria
        boxes = []
        kps = []

        # boxes: intentar accedir a res.boxes.xyxy
        try:
            # .boxes.xyxy existeix en versions modernes
            xyxy = res.boxes.xyxy.cpu().numpy() if hasattr(res.boxes, "xyxy") else None
            confs = res.boxes.conf.cpu().numpy() if hasattr(res.boxes, "conf") else None
        except Exception:
            xyxy = None
            confs = None

        # keypoints: res.keypoints podria existir
        keypoints_list = None
        try:
            if hasattr(res, "keypoints") and res.keypoints is not None:
                try:
                    kp_data = None
                    if hasattr(res.keypoints, "xy"):
                        kp_data = res.keypoints.xy.cpu().numpy()
                    elif hasattr(res.keypoints, "xyxyn"):
                        kp_data = res.keypoints.xyxyn.cpu().numpy()
                    elif hasattr(res.keypoints, "data"):
                        kp_data = res.keypoints.data.cpu().numpy()
                    else:
                        try:
                            kp_data = res.keypoints.cpu().numpy()
                        except Exception:
                            kp_data = None

                    if kp_data is not None:
                        keypoints_list = kp_data
                except Exception:
                    keypoints_list = None
        except Exception:
            keypoints_list = None

        num_dets = 0
        try:
            if xyxy is not None:
                num_dets = len(xyxy)
            elif keypoints_list is not None:
                num_dets = len(keypoints_list)
            else:
                num_dets = len(res.boxes) if hasattr(res, "boxes") else 0
        except Exception:
            num_dets = 0

        # Recorrer deteccions indexades
        for i in range(num_dets):
            bbox = None
            kp = None
            try:
                if xyxy is not None and i < len(xyxy):
                    x1, y1, x2, y2 = xyxy[i].tolist()
                    bbox = (int(x1), int(y1), int(x2), int(y2))
                if keypoints_list is not None and i < len(keypoints_list):
                    arr = keypoints_list[i]
                    import numpy as np
                    arr = np.array(arr)
                    if arr.ndim == 1 and arr.size % 3 == 0:
                        arr = arr.reshape((-1,3))
                    kp = arr  # cada fila: (x,y,conf)
            except Exception:
                pass

            detections.append({'bbox': bbox, 'keypoints': kp})

    except Exception as e:
        print("Error al detectar amb YOLO:", e)
        traceback.print_exc()

    return detections

# === Determinar si una detecció (persona) està tumbada ===
def detection_is_lying(det):
    
    # ... (càlculs inicials del BBox) ...
    kp = det.get('keypoints', None)
    bbox = det.get('bbox', None)
    if bbox is None:
        return False
        
    x1, y1, x2, y2 = bbox
    bbox_w = max(1, x2 - x1)  # Amplada del BBox
    bbox_h = max(1, y2 - y1)  # Alçada del BBox

    try:
        import numpy as np
        # Comprovem mida kp (necessitem almenys fins al maluc - índex 12)
        if kp is None or kp.shape[0] < 13:
            # Si no tenim keypoints, només depenem del BBox Aspect Ratio
            pass
        else:
            # Extraiem punts d'interès (5=left_shoulder, 6=right_shoulder)
            left_shoulder = kp[5]
            right_shoulder = kp[6]

            # Només procedim si tenim una confiança raonable en les espatlles
            min_conf = 0.2
            if left_shoulder[2] >= min_conf and right_shoulder[2] >= min_conf:
                
                # Calculem l'angle de la línia que uneix les dues espatlles respecte a l'horitzontal
                dx = right_shoulder[0] - left_shoulder[0]
                dy = right_shoulder[1] - left_shoulder[1]
                
                if abs(dx) > 1: 
                    angle_rad = np.arctan2(dy, dx)
                    angle_deg = np.abs(np.degrees(angle_rad))
                    
                    effective_angle = min(angle_deg, 180 - angle_deg)

                    ANGLE_THRESH = 45 # Llindar: si l'angle és < 30 graus, està horitzontal
                    if effective_angle < ANGLE_THRESH:
                        return True

                # Aquest criteri busca persones esteses panxa amunt/avall (no de costat)
                left_hip = kp[11]
                right_hip = kp[12]
                if left_hip[2] >= min_conf and right_hip[2] >= min_conf:
                    shoulders_y_diff = abs(left_shoulder[1] - right_shoulder[1])
                    hips_y_diff = abs(left_hip[1] - right_hip[1])

                    if (shoulders_y_diff / bbox_h) < KP_Y_DIFF_RATIO and \
                       (hips_y_diff / bbox_h) < KP_Y_DIFF_RATIO:
                        return True

    except Exception as e:
        pass # Continuem amb el criteri del BBox si falla l'anàlisi de keypoints

    ASPECT_RATIO_THRESH = 1.6
    if (bbox_w / bbox_h) > ASPECT_RATIO_THRESH:
        return True

    return False

# === Funcions BBDD (cameres, detecions, caidas, estado_camara) ===
def update_cameres(ip_cam, persones):
    try:
        conn = connection()
        cursor = conn.cursor()

        ara = dt.now()

        cursor.execute("SELECT persones FROM cameres WHERE ip = %s", (ip_cam,))
        row = cursor.fetchone()

        if row is None:
            cursor.execute(
                "INSERT INTO cameres (camera, ip, persones, ultim_heartbeat) VALUES (%s, %s, %s, %s)",
                ("cam_" + ip_cam.replace(".", "_"), ip_cam, persones, ara)
            )
        else:
            cursor.execute(
                "UPDATE cameres SET persones = %s, ultim_heartbeat = %s WHERE ip = %s",
                (persones, ara, ip_cam)
            )

        conn.commit()

    except Exception as e:
        print("Error update_cameres:", e)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

def save_detection(ip_cam, num_persones, filename):
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO detecions (date, num_personas, ruta_imatge, ubicacion) VALUES (%s, %s, %s, %s)",
            (dt.now(), num_persones, filename, ip_cam)
        )
        conn.commit()
    except Exception as e:
        print("Error save_detection:", e)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
def registrar_caida(ip, imagen):
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO caidas (fecha, ip, ruta_imatge) VALUES (%s, %s, %s)",
            (dt.now(), ip, imagen)
        )
        conn.commit()
        
        enviar_alerta_mqtt(ip, resolta=False) 
        
    except Exception as e:
        print("Error registrar_caida:", e)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

def gestionar_alertes_estat(ip_cam, any_lying):
    cal_enviar_resolta = False # Variable per recordar si s'ha d'enviar l'avís
    
    try:
        conn = connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT tumbat, alerta_enviada FROM estat_camera WHERE ip = %s", (ip_cam,))
        row = cursor.fetchone()
        
        nou_estat = 1 if any_lying else 0

        if row:
            estat_actual = row[0]
            alerta_enviada = row[1]
            
            if nou_estat != estat_actual:
                cursor.execute("UPDATE estat_camera SET tumbat = %s, hora = %s WHERE ip = %s", (nou_estat, dt.now(), ip_cam))
                
                # Si s'aixeca i hi havia alerta crítica
                if nou_estat == 0 and alerta_enviada == 1:
                    cal_enviar_resolta = True # Apuntem que ho hem d'enviar!
                    cursor.execute("UPDATE estat_camera SET alerta_enviada = 0 WHERE ip = %s", (ip_cam,))
        else:
            cursor.execute("INSERT INTO estat_camera (ip, tumbat, hora, alerta_enviada) VALUES (%s, %s, %s, 0)",
                           (ip_cam, nou_estat, dt.now()))

        conn.commit()
    except Exception as e:
        print("Error gestionant alertes:", e)
    finally:
        try:
            cursor.close()
            conn.close() 
        except Exception:
            pass
            
    # FORA DE LA BASE DE DADES: Enviem l'MQTT si calia
    if cal_enviar_resolta:
        enviar_alerta_mqtt(ip_cam, resolta=True)


def check_caida_prolongada_and_register(ip_cam, filename):
    cal_registrar_caida = False # Variable per recordar si hem d'enviar l'avís
    
    try:
        conn = connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT tumbat, hora, alerta_enviada FROM estat_camera WHERE ip = %s", (ip_cam,))
        row = cursor.fetchone()
        
        if not row:
            return False
            
        tumbat, hora, alerta_enviada = row
        
        if tumbat == 1 and alerta_enviada == 0:
            temps_tumbat = (dt.now() - hora).total_seconds()
            
            if temps_tumbat >= LYING_TIME_SECONDS:
                cal_registrar_caida = True 
                cursor.execute("UPDATE estat_camera SET alerta_enviada = 1 WHERE ip = %s", (ip_cam,))
                conn.commit()
                
    except Exception as e:
        print("Error check_caida:", e)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
            
    if cal_registrar_caida:
        registrar_caida(ip_cam, filename) 
        return True
        
    return False

# === Endpoint principal /upload ===
@app.route('/upload', methods=['POST'])
def upload():
#Endpoint principal que rep les imatges de l'ESP32-CAM. Coordina tot el flux: recepció, rotació, detecció d'IA, actualització de la BBDD i gestió d'alertes.

    if request.headers.get('X-API-KEY') != config.API_KEY:
        return "Accés denegat", 401

    try:
        img_data = request.data
        if not img_data:
            return "No data received", 400

        if not img_data.startswith(b'\xff\xd8'):
            print(f"Alerta: Fitxer no vàlid rebut des de la IP {request.remote_addr}")
            return "Format invàlid. Només s'accepten imatges JPEG.", 400

        # Generar nom de fitxer basat en la data i hora actual
        filename = dt.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        ip_cam = request.remote_addr

        # Guardar la imatge binària rebuda
        with open(filepath, 'wb') as f:
            f.write(img_data)

        # Processar la imatge (llegir i rotar)
        frame = load_image(filepath)

        # Executar l'anàlisi d'IA (Detecció de persones i esquelets)
        detections = detect_persons_and_keypoints(frame)

        num_persones = len(detections)
        save_detection(ip_cam, num_persones, filename)
        update_cameres(ip_cam, num_persones)
        
        # Comprovar si algun dels individus detectats està en posició de caiguda
        any_lying = False
        if num_persones > 0:
            for det in detections:
                try:
                    if detection_is_lying(det):
                        any_lying = True                    
                        break
                except Exception:
                    continue
        else: 
            any_lying = False
            
        # =======================================================
        # --- NOVA LÒGICA DE CENSURA BASADA EN YOLO ---
        # =======================================================
        if num_persones > 0:
            h_img, w_img = frame.shape[:2]
            
            for det in detections:
                kp = det.get('keypoints')
                # Comprovem que tenim punts clau i que n'hi ha almenys 5
                if kp is not None and len(kp) >= 5:
                    punts_cara = kp[0:5] # Nas, ulls i orelles
                    
                    punts_valids = []
                    for punt in punts_cara:
                        # Comprovem quants valors té el punt per evitar errors
                        if len(punt) >= 3:
                            x, y, conf = punt[0], punt[1], punt[2]
                        elif len(punt) == 2:
                            x, y = punt[0], punt[1]
                            conf = 1.0 # Si no hi ha confiança, assumim que el punt és vàlid (100%)
                        else:
                            continue # Si el punt ve buit o corrupte, el saltem
                            
                        if conf > 0.3: # Només fiar-nos dels punts clars
                            punts_valids.append((int(x), int(y)))                    
                    if len(punts_valids) >= 2:
                        xs = [p[0] for p in punts_valids]
                        ys = [p[1] for p in punts_valids]
                        
                        min_x, max_x = min(xs), max(xs)
                        min_y, max_y = min(ys), max(ys)
                        
                        amplada_punts = max(10, max_x - min_x)
                        alcada_punts = max(10, max_y - min_y)
                        
                        marge_x = int(amplada_punts * 0.8)
                        marge_y_dalt = int(alcada_punts * 1.5)
                        marge_y_baix = int(alcada_punts * 1.0)
                        
                        startX = max(0, min_x - marge_x)
                        startY = max(0, min_y - marge_y_dalt)
                        endX = min(w_img, max_x + marge_x)
                        endY = min(h_img, max_y + marge_y_baix)
                        
                        w_cara = endX - startX
                        h_cara = endY - startY
                        
                        if w_cara > 0 and h_cara > 0:
                            # Pixelat
                            cara = frame[startY:endY, startX:endX]
                            cara_petita = cv2.resize(cara, (10, 10), interpolation=cv2.INTER_LINEAR)
                            cara_pixelada = cv2.resize(cara_petita, (w_cara, h_cara), interpolation=cv2.INTER_NEAREST)
                            frame[startY:endY, startX:endX] = cara_pixelada

        # Ara que la imatge (frame) ja té la censura aplicada, la guardem definitivament
        cv2.imwrite(filepath, frame)
        # Creem una versió "en viu" que s'anirà sobreescrivint de forma segura
        latest_temp = os.path.join(UPLOAD_FOLDER, f"temp_{ip_cam}.jpg")
        latest_final = os.path.join(UPLOAD_FOLDER, f"latest_{ip_cam}.jpg")
        
        cv2.imwrite(latest_temp, frame) # Escrivim al temporal
        os.replace(latest_temp, latest_final) # Substitució atòmica, evita errors de lectura
        
        # Gestionar els estats de l'alerta de Telegram
        gestionar_alertes_estat(ip_cam, any_lying)
            
        # Comprovar si la caiguda és crítica (prolongada)
        if any_lying:
            if check_caida_prolongada_and_register(ip_cam, filename):
                print(f"CAÍDA PROLONGADA DETECTADA per {ip_cam}")
        
        return "OK", 200
        
    except Exception as e:
        print("Error general upload:", e)
        traceback.print_exc()
        return str(e), 500

# === Endpoint pel Heartbeat (Batec de vida) ===
@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    ip_cam = request.remote_addr
    ara = dt.now()
    
    if request.headers.get('X-API-KEY') != config.API_KEY:
        return "Accés denegat", 401

    try:
        conn = connection()
        cursor = conn.cursor()
        
        # Comprovem si la càmera ja existeix a la BD
        cursor.execute("SELECT ip FROM cameres WHERE ip = %s", (ip_cam,))
        if cursor.fetchone() is None:
            # Si és nova, la registrem (amb 0 persones per defecte)
            cursor.execute(
                "INSERT INTO cameres (camera, ip, persones, ultim_heartbeat) VALUES (%s, %s, %s, %s)",
                ("cam_" + ip_cam.replace(".", "_"), ip_cam, 0, ara)
            )
        else:
            # Si ja existeix, NOMÉS actualitzem la columna ultim_heartbeat
            cursor.execute(
                "UPDATE cameres SET ultim_heartbeat = %s WHERE ip = %s",
                (ara, ip_cam)
            )
            
        conn.commit()
        return "Batec rebut", 200
        
    except Exception as e:
        print("Error al heartbeat:", e)
        return "Error intern", 500
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=5001)
