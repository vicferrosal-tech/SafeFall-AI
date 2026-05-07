# README — SAFEFALL AI

## Descripció del projecte

**SAFEFALL AI** és un sistema intel·ligent basat en visió artificial i intel·ligència artificial capaç de detectar caigudes i analitzar la densitat de persones en temps real mitjançant una càmera ESP32-CAM i un servidor de processament basat en Raspberry Pi.

El projecte està orientat principalment a residències, hospitals i centres assistencials, amb l’objectiu de millorar la seguretat de les persones i facilitar una resposta ràpida davant situacions de risc.

El sistema combina tecnologies de:

* Intel·ligència Artificial 
* Visió Artificial 
* IoT 
* Big Data 
* Ciberseguretat 

---

#  Objectius principals

* Detectar caigudes automàticament en temps real.
* Analitzar la densitat de persones dins d’un espai.
* Enviar alertes automàtiques davant incidències.
* Garantir la privacitat de les dades mitjançant pixelat i mesures RGPD.
* Mostrar estadístiques i dades en un dashboard interactiu.
* Crear una arquitectura escalable i adaptable a entorns reals.

---

#  Tecnologies utilitzades

## Backend

* Python 3
* Flask
* OpenCV
* YOLOv8
* MariaDB
* MQTT (Mosquitto)

## Hardware

* ESP32-CAM
* Raspberry Pi 4
* Sensors PIR i sensors de so
* Carcassa impresa en 3D

## Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

## Altres eines

* Arduino IDE
* Visual Studio Code
* GitHub
* Postman
* Tinkercad
* Cura / PrusaSlicer

---

#  Arquitectura del sistema

```text
ESP32-CAM
   │
   │ Wi-Fi / HTTPS
   ▼
Servidor Flask (Raspberry Pi)
   │
   ├── Processament IA (YOLOv8 + OpenCV)
   ├── Base de dades MariaDB
   ├── Dashboard web
   └── Sistema d’alertes MQTT
            │
            ▼
      Aplicació mòbil
```

---

#  Funcionalitats principals

##  Detecció de caigudes

El sistema analitza la posició i moviment de les persones mitjançant IA per detectar possibles caigudes.

##  Densitat de persones

Monitoratge del nombre de persones dins d’una zona per detectar aglomeracions o situacions de risc.

##  Dashboard interactiu

Visualització en temps real de:

* Alertes crítiques
* Activitat del sistema
* Estat de les càmeres
* Gràfiques i estadístiques

##  Sistema Heartbeat

Control de connexió de les càmeres per detectar errors o desconnexions.

##  Compliment RGPD

* Pixelat automàtic de rostres
* Xifrat HTTPS
* Sistema d’autenticació segura
* Emmagatzematge protegit

##  Alertes en temps real

Enviament instantani de notificacions a l’aplicació mòbil via MQTT.

---

#  Seguretat  implementada

* HTTPS amb SSL/TLS
* Xifrat de contrasenyes
* Sistema de login segur
* Protecció de dades personals
* Compliment del Reglament General de Protecció de Dades (RGPD)

---

#  Big Data i estadístiques

El sistema genera estadístiques automàtiques sobre:

* Nombre de caigudes
* Zones amb més incidències
* Activitat diària
* Estat de les càmeres
* Historial d’alertes

Les dades es representen mitjançant gràfiques interactives amb Chart.js.

---

#  Instal·lació del projecte

##  1. Clonar el repositori

```bash
git clone https://github.com/usuari/safefall-ai.git
cd safefall-ai
```

---

##  2. Crear entorn virtual

```bash
python -m venv venv
```

### Linux/Mac

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Instal·lar dependències

```bash
pip install -r requirements.txt
```

---

##  4. Configurar la base de dades

Crear la base de dades MariaDB i importar els scripts SQL.

```sql
CREATE DATABASE safefall_ai;
```

---

##  Executar el servidor Flask

```bash
python web.py
```

---

#  Estructura del projecte

```text
SAFEFALL_AI/
│
├── web.py
├── usuaris.py
├── rebuda_imatges.py
├── requirements.txt
├── static/
├── templates/
│   ├── index.html
│   ├── galeria.html
│   └── login.html
├── database/
├── models/
├── captures/
└── README.md
```

---

#  Futures millores

* Aplicació mòbil completa
* Integració amb més sensors IoT
* Millora del model d’IA
* Sistema multi-càmera
* Notificacions push avançades
* Processament distribuït

---

#  Relació amb els ODS

Aquest projecte contribueix als Objectius de Desenvolupament Sostenible:

* ODS 3 — Salut i benestar
* ODS 9 — Innovació i infraestructures
* ODS 11 — Ciutats sostenibles
* ODS 16 — Seguretat i privacitat

---

#  Autors

* Victoria Fernández
* Isaac Dominguez


---

#  Llicència

Aquest projecte té finalitat educativa i acadèmica.
L’ús comercial requereix autorització dels autors.

---

#  SAFEFALL AI

> “SafeFall AI — La seguretat que no descansa.”
