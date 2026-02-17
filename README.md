🏠 Real Estate Hunter: Idealista Automation 🚀
Smart Real Estate Hunter es un sistema de monitorización inteligente diseñado para capturar oportunidades en el mercado inmobiliario de Idealista. El sistema está optimizado para ejecutarse de forma persistente en Windows mediante un lanzador automatizado.

🧠 Funcionamiento del Sistema
Lanzador Automatizado (.bat): El proyecto cuenta con un archivo ejecutable de Windows que gestiona el arranque del entorno y el script de Python, asegurando que el bot esté siempre operativo.

Rastreo Dinámico: Utiliza Selenium y BeautifulSoup para navegar por las múltiples páginas de resultados de Idealista, simulando un comportamiento humano para evitar bloqueos.

Persistencia en MongoDB: Todos los datos se almacenan en una base de datos NoSQL. Esto permite al bot "recordar" qué pisos ya ha visto y detectar instantáneamente si un propietario ha bajado el precio.

Alertas Push: Las novedades y bajadas de precio se envían directamente a un canal de Telegram mediante mensajes enriquecidos en HTML.

✨ Características Técnicas
Detección de Bajadas de Precio: Compara el precio actual con el histórico guardado en MongoDB.

Gestión de Paginación: El bot no se queda solo en la primera página; recorre todo el listado de búsqueda.

Base de Datos NoSQL: Uso de PyMongo para una gestión de datos rápida y escalable.

Modo Silencioso: Configurado para ejecutarse en segundo plano.

🛠️ Stack Tecnológico
Lenguaje: Python 3.x

Automatización: Selenium & Batch Scripting

Base de Datos: MongoDB

Notificaciones: Telegram Bot API

🚀 Cómo ponerlo en marcha
Configuración inicial:

Instala las librerías necesarias: pip install selenium beautifulsoup4 pymongo requests

Asegúrate de tener instalado MongoDB (local o Atlas).

Uso:

No necesitas ejecutar comandos complejos en la consola. Simplemente haz doble clic en el archivo:

Lanzador_Bot.bat

Este archivo se encarga de abrir el script y mantener el bot rastreando el mercado.

📋 Ejemplo de Alerta en Telegram
🏠 ¡NUEVO!
💰 1.100 €/mes
📍 Chamberí, Madrid
🔗 [Ver Casa en Idealista]
