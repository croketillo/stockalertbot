from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import yfinance as yf
import logging
import json
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configura el token de tu bot de Telegram y la contraseña desde el archivo .env
TOKEN = os.getenv("TELEGRAM_TOKEN")
PASSWORD = os.getenv("BOT_PASSWORD")

if not TOKEN:
    raise ValueError("No se ha encontrado la variable de entorno TELEGRAM_TOKEN.")
if not PASSWORD:
    raise ValueError("No se ha encontrado la variable de entorno BOT_PASSWORD.")

authorized_users = set()

# Diccionario para almacenar configuraciones de precios
precio_config = {}

# Archivo para almacenar la configuración
CONFIG_FILE = 'config.json'

# Configuración del registro en un archivo
logging.basicConfig(filename='stocks_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    global precio_config, authorized_users
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                # Convertir claves de cadena de vuelta a tuplas
                precio_config = {eval(k): v for k, v in loaded_config.get('precio_config', {}).items()}
                authorized_users = set(loaded_config.get('authorized_users', []))
        except (json.JSONDecodeError, SyntaxError) as e:
            logging.error(f"Error al decodificar el archivo de configuración: {e}. Iniciando con configuración vacía.")
            precio_config = {}
            authorized_users = set()
    else:
        precio_config = {}
        authorized_users = set()

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        # Convertir claves de tupla a cadenas
        serializable_config = {str(k): v for k, v in precio_config.items()}
        json.dump({
            'precio_config': serializable_config,
            'authorized_users': list(authorized_users)
        }, f)

def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        '¡Hola! Este es el bot de avisos de precios de mercado.\n\n'
        '[🔑] /auth <PASSWORD>\t para autorizar el uso del bot.\n'
        '[📌] /set <TICKER> <TARGET PRICE> <UP/DOWN>\t para configurar una alerta.\n'
        '[⚙️] /config\t para ver las configuraciones existentes.\n'
        '[❌] /remove <TICKER>\t para eliminar las alertas de ese Ticker.\n'
        '[❓] /help para obtener ayuda.'
    )
    update.message.reply_text(welcome_text)

def help(update: Update, context: CallbackContext) -> None:
    help_text = (
        'HELP:\n\n'
        '[🔑] /auth <PASSWORD>\t para autorizar el uso del bot.\n'
        '[📌] /set <TICKER> <TARGET PRICE> <UP/DOWN>\t para configurar una alerta.\n'
        '[⚙️] /config\t para ver las configuraciones existentes.\n'
        '[❌] /remove <TICKER>\t para eliminar las alertas de ese Ticker.\n'
        '[❓] /help\t para obtener ayuda.'
    )
    update.message.reply_text(help_text)

def auth(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    args = context.args

    if len(args) != 1:
        update.message.reply_text("❗ Uso incorrecto. Ejemplo: /auth mysecretpassword")
        return

    password = args[0]

    if password == PASSWORD:
        authorized_users.add(chat_id)
        save_config()
        update.message.reply_text("✅ Autorización exitosa. Ahora puedes usar el bot.")
    else:
        update.message.reply_text("❗ Contraseña incorrecta.")

def set_price(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    if chat_id not in authorized_users:
        update.message.reply_text("❗ No estás autorizado para usar este comando. Usa /auth <PASSWORD> para autorizarte.")
        return

    args = context.args

    if len(args) != 3:
        update.message.reply_text("❗ Uso incorrecto. Ejemplo: /set AAPL 150.00 UP")
        return

    ticker = args[0].upper()
    try:
        target_price = float(args[1])
    except ValueError:
        update.message.reply_text("❗ El precio objetivo debe ser un número.")
        return

    direction = args[2].upper()

    if direction not in ["UP", "DOWN"]:
        update.message.reply_text("❗ La dirección debe ser UP o DOWN.")
        return

    precio_config[(chat_id, ticker)] = {"target_price": target_price, "direction": direction}
    save_config()
    update.message.reply_text(f"🔧 Aviso configurado para {ticker} cuando {direction.lower()} a 🪙{target_price}.")

def remove_price(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    if chat_id not in authorized_users:
        update.message.reply_text("❗ No estás autorizado para usar este comando. Usa /auth <PASSWORD> para autorizarte.")
        return

    args = context.args

    if len(args) != 1:
        update.message.reply_text("❗ Uso incorrecto. Ejemplo: /remove AAPL")
        return

    ticker = args[0].upper()

    if (chat_id, ticker) in precio_config:
        del precio_config[(chat_id, ticker)]
        save_config()
        update.message.reply_text(f"❌ Aviso para {ticker} eliminado.")
    else:
        update.message.reply_text(f"❗ No se encontró ningún aviso para {ticker}.")

def view_config(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    if chat_id not in authorized_users:
        update.message.reply_text("❗ No estás autorizado para usar este comando. Usa /auth <PASSWORD> para autorizarte.")
        return

    config_text = "\n".join([f"📌 {ticker}: Alerta en precio -> {config['target_price']} direccion {config['direction']}" for (cid, ticker), config in precio_config.items() if cid == chat_id])

    if config_text:
        update.message.reply_text(f"⚙️ Configuración actual:\n\n{config_text}")
    else:
        update.message.reply_text("⚙️ No hay configuración actual.")

def check_prices(context: CallbackContext) -> None:
    for (chat_id, ticker), config in precio_config.copy().items():
        try:
            logging.info(f"Obteniendo información para el ticker {ticker}")
            ticker_info = yf.Ticker(ticker)
            stock_info = ticker_info.info

            # Verificar si se obtuvo información válida
            if 'currentPrice' not in stock_info:
                raise ValueError(f"No se encontró el precio actual para {ticker}")

            current_price = float(stock_info["currentPrice"])

            # Registro del precio actual para fines de depuración
            logging.info(f"{ticker} - Precio actual: {current_price}")

            if config["direction"] == "UP" and current_price >= config["target_price"]:
                message = f"📈 [!] El precio de {ticker} ha alcanzado o superado {config['target_price']}. Precio actual: {current_price}"
                context.bot.send_message(chat_id=chat_id, text=message)
                logging.info(f"{ticker} - Alerta de precio UP: {current_price}")

                del precio_config[(chat_id, ticker)]
                save_config()

            elif config["direction"] == "DOWN" and current_price <= config["target_price"]:
                message = f"📉 [!] El precio de {ticker} ha caído a {config['target_price']}. Precio actual: {current_price}"
                context.bot.send_message(chat_id=chat_id, text=message)
                logging.info(f"{ticker} - Alerta de precio DOWN: {current_price}")

                del precio_config[(chat_id, ticker)]
                save_config()

        except ValueError as ve:
            logging.error(f"❗ Error de valor al obtener información para {ticker}: {ve}")
        except Exception as e:
            logging.error(f"❗ Error al obtener información para {ticker}: {e}")

if __name__ == '__main__':
    load_config()
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("auth", auth))
    dispatcher.add_handler(CommandHandler("set", set_price))
    dispatcher.add_handler(CommandHandler("remove", remove_price))
    dispatcher.add_handler(CommandHandler("config", view_config))

    updater.job_queue.run_repeating(check_prices, interval=60, first=0)

    updater.start_polling()
    updater.idle()
