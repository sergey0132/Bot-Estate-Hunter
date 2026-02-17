import time
import requests  # Para Telegram
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os

# --- 1. CONFIGURACIÓN DE TELEGRAM (¡RELLENA ESTO!) ---

# --- CONFIGURACIÓN DE CREDENCIALES ---

# Sustituye estos valores por tus datos reales
TOKEN = "TU_TOKEN_AQUÍ"  # Ejemplo: '123456:ABC-DEF...'
CHAT_ID = "TU_CHAT_ID_AQUÍ"       # Ejemplo: '-100123456789'

# URL de búsqueda que quieres rastrear
url_objetivo = "URL_DE_IDEALISTA_CON_FILTROS_AQUÍ"

def enviar_alerta(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id":CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
        print("📨 Notificación enviada a Telegram.")
    except Exception as e:
        print(f"❌ Error enviando Telegram: {e}")

# --- 2. CONEXIÓN A MONGODB ---

# Usa "mongodb://localhost:27017/" para pruebas locales
client = MongoClient("TU_CONEXION_MONGODB")
db = client['cazador_pisos']
collection = db['anuncios']

# --- 3. CONEXIÓN AL NAVEGADOR (Modo Copiloto) ---

print("🔗 Conectando al navegador abierto...")
edge_options = Options()

# OPCIÓN A: Conexión a navegador abierto (Recomendado para saltar bloqueos)
# Requiere abrir Edge con: msedge.exe --remote-debugging-port=9222
edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# OPCIÓN B: Modo normal (Descomenta las líneas de abajo si prefieres que el bot abra su propia ventana)
# edge_options.add_argument("--start-maximized")
# edge_options.add_argument("--disable-blink-features=AutomationControlled")

# Asegúrate de que el driver esté en la misma carpeta o indica la ruta
ruta_driver = os.path.join(os.getcwd(), "msedgedriver.exe") 
service = Service(executable_path=ruta_driver)
driver = webdriver.Edge(service=service, options=edge_options)
print("✅ Conectado. Analizando la página actual...")

# --- AÑADE ESTO AQUÍ (ANTES DEL BUCLE O DEL ESCANEO) ---

# 1. Definimos la URL
url_objetivo = ""# aqui ponemos el url con los filtros ya puestos en la pagina
while True:
        print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] --- INICIANDO RONDA DE ESCANEO ---")
        
        # 1. NAVEGACIÓN INTELIGENTE
        try:
            # Si no estamos en la URL, vamos a ella. Si ya estamos, solo refrescamos.
            if driver.current_url != url_objetivo:
                driver.get(url_objetivo)
                time.sleep(4)
                
                # Esquivamos el muro de cookies de forma automática
                try:
                    driver.find_element(By.ID, "didomi-notice-agree-button").click()
                    time.sleep(2)
                except:
                    pass # Si no sale el botón, seguimos adelante

        except Exception as e:
            print(f"⚠️ Error navegando: {e}")
            time.sleep(10)
            continue

        pagina_actual = 1
        
        # --- BUCLE DE RASTREO (Recorremos todas las páginas de resultados) ---
        while True: 
            try:
                print(f"📖 Analizando PÁGINA {pagina_actual}...")
                
                # Simulamos scroll humano para que Idealista cargue todas las imágenes y datos
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3) 
                
                # Extraemos el código HTML y buscamos cada "caja" de piso (article.item)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                pisos = soup.find_all('article', class_='item')
                
                print(f"   └── Encontrados {len(pisos)} anuncios en esta página.")

                # --- PROCESAMIENTO DE DATOS (Analizamos piso por piso) ---
                for i, piso in enumerate(pisos):
                    try:
                        # Extraemos Título, Link, Precio y Detalles (m2, habitaciones)
                        titulo_tag = piso.find('a', class_='item-link')
                        if not titulo_tag: continue
                        
                        link = f"https://www.idealista.com{titulo_tag['href']}"
                        ubicacion = titulo_tag.text.strip()

                        # Limpiamos el precio: de "1.200 €/mes" a un número puro (1200)
                        precio_tag = piso.find('span', class_='item-price')
                        precio_texto = precio_tag.text.strip() if precio_tag else "0"
                        try:
                            precio_num = int(precio_texto.replace('.', '').replace('€', '').replace('/mes', '').strip())
                        except:
                            precio_num = 0

                        # 2. GESTIÓN DE BASE DE DATOS (MongoDB)
                        id_piso = piso.get('data-element-id') or f"unknown-{i}-{pagina_actual}"
                        piso_db = collection.find_one({"_id": id_piso})

                        # CASO A: Es un piso que no conocíamos (¡Oportunidad nueva!)
                        if not piso_db:
                            print(f"   ✨ NUEVO: {ubicacion[:25]}... ({precio_num}€)")
                            doc = {
                                "_id": id_piso, "ubicacion": ubicacion, "precio": precio_num,
                                "link": link, "fecha": datetime.now(), 
                                "historial": [{"p": precio_num, "f": datetime.now()}]
                            }
                            collection.insert_one(doc)
                            
                            # Notificamos al móvil por Telegram
                            msg = (f"🏠 <b>¡NUEVO!</b>\n💰 <b>{precio_texto}</b>\n📍 {ubicacion}\n"
                                f"🔗 <a href='{link}'>Ver Casa</a>")
                            enviar_alerta(msg)
                            time.sleep(3) 

                        # CASO B: El piso ya lo conocíamos, pero... ¡Ha bajado de precio!
                        elif precio_num != 0 and precio_num < piso_db['precio']:
                            print(f"   📉 BAJADA: {ubicacion[:25]}... ({piso_db['precio']} -> {precio_num})")
                            collection.update_one({"_id": id_piso}, 
                                {"$set": {"precio": precio_num}, 
                                "$push": {"historial": {"p": precio_num, "f": datetime.now()}}})
                            
                            msg = (f"📉 <b>¡BAJADA!</b>\nAntes: {piso_db['precio']}€ ➡️ <b>{precio_num}€</b>\n"
                                f"📍 {ubicacion}\n🔗 <a href='{link}'>Ver Oportunidad</a>")
                            enviar_alerta(msg)
                            time.sleep(4)
                    
                    except Exception as e:
                        continue 

                # --- PAGINACIÓN (Buscamos el botón "Siguiente") ---
                try:
                    boton_next = driver.find_element(By.CSS_SELECTOR, "a.icon-arrow-right-after")
                    if boton_next:
                        driver.execute_script("arguments[0].click();", boton_next)
                        time.sleep(5) # Pausa para que cargue la siguiente página
                        pagina_actual += 1
                    else:
                        break 
                except:
                    break

            except Exception as e:
                print(f"❌ Error crítico: {e}")
            break
        print("💤 Ronda terminada. Durmiendo 10 minutos...") # acordamnos que el tiuempo se mide en segundos y se puede cambiar en la linea de abajo
        time.sleep(600)