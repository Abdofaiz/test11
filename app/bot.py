import os
import json
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Configuration
TELEGRAM_TOKEN = os.environ.get('7751238432:AAEfCQ-LS5YujqVU9ZvPNPHn2fVqe6oLEMU')
ADMIN_USERNAME = "faizvpn"  # Your Telegram username
CONFIG_PATH = '/etc/v2ray/config.json'
SERVER_URL = "https://v2ra-panel-728381334696.us-central1.run.app"

def is_admin(username):
    return username == ADMIN_USERNAME

def read_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def write_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    os.system('kill -SIGHUP $(pidof v2ray)')

def generate_vless_link(user_id, email):
    server_domain = SERVER_URL.replace('https://', '').replace('http://', '')
    return f"vless://{user_id}@{server_domain}:443?encryption=none&security=tls&type=ws&path=%2Fvless&host={server_domain}#{email}"

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['👥 Create User', '📋 List Users'],
        ['❌ Delete User', '📊 Server Status'],
        ['ℹ️ Help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "🚀 Welcome to VLESS Manager Bot!\n\n"
        "Select an option from the menu below:\n"
        "• 👥 Create User - Add new VLESS user\n"
        "• 📋 List Users - Show all users\n"
        "• ❌ Delete User - Remove user\n"
        "• 📊 Server Status - Check server status\n"
        "• ℹ️ Help - Show help message"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 Available Commands:\n\n"
        "/start - Start the bot\n"
        "/create - Create new user\n"
        "/list - List all users\n"
        "/delete - Delete user\n"
        "/status - Server status\n"
        "/help - Show this message\n\n"
        "Or use the menu buttons below 👇"
    )
    await update.message.reply_text(help_text)

async def create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.username):
        await update.message.reply_text("⛔️ You are not authorized to use this command.")
        return
    
    await update.message.reply_text("Please send the email for the new user:")
    context.user_data['waiting_for'] = 'email'

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for') != 'email':
        return
    
    email = update.message.text
    config = read_config()
    
    if any(client.get('email') == email for client in config['inbounds'][0]['settings']['clients']):
        await update.message.reply_text(f"❌ User {email} already exists!")
        return

    new_user = {
        'id': str(uuid.uuid4()),
        'email': email,
        'flow': ""
    }
    
    config['inbounds'][0]['settings']['clients'].append(new_user)
    write_config(config)

    vless_link = generate_vless_link(new_user['id'], email)
    
    response = (
        f"✅ New user created successfully!\n\n"
        f"📧 Email: {email}\n"
        f"🆔 UUID: {new_user['id']}\n\n"
        f"🔗 VLESS Link:\n`{vless_link}`\n\n"
        f"📱 Configuration:\n"
        f"Address: {SERVER_URL}\n"
        f"Port: 443\n"
        f"Protocol: vless\n"
        f"Path: /vless\n"
        f"TLS: Enabled"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')
    context.user_data['waiting_for'] = None

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.username):
        await update.message.reply_text("⛔️ You are not authorized to use this command.")
        return

    config = read_config()
    clients = config['inbounds'][0]['settings']['clients']
    
    if not clients:
        await update.message.reply_text("No users found.")
        return

    user_list = "👥 Current Users:\n\n"
    for idx, client in enumerate(clients, 1):
        user_list += f"{idx}. 📧 {client.get('email', 'No email')}\n   🆔 {client['id']}\n\n"
    
    await update.message.reply_text(user_list)

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.username):
        await update.message.reply_text("⛔️ You are not authorized to use this command.")
        return

    config = read_config()
    clients = config['inbounds'][0]['settings']['clients']
    
    if not clients:
        await update.message.reply_text("No users to delete.")
        return

    keyboard = []
    for client in clients:
        keyboard.append([InlineKeyboardButton(
            f"📧 {client.get('email', 'No email')}",
            callback_data=f"delete_{client.get('email')}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select user to delete:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("delete_"):
        email = query.data.replace("delete_", "")
        config = read_config()
        clients = config['inbounds'][0]['settings']['clients']
        
        config['inbounds'][0]['settings']['clients'] = [
            c for c in clients if c.get('email') != email
        ]
        
        write_config(config)
        await query.edit_message_text(f"✅ User {email} has been deleted.")

async def server_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.username):
        await update.message.reply_text("⛔️ You are not authorized to use this command.")
        return

    config = read_config()
    total_users = len(config['inbounds'][0]['settings']['clients'])
    
    status = (
        "📊 Server Status\n\n"
        f"🌐 Server: {SERVER_URL}\n"
        f"👥 Total Users: {total_users}\n"
        "✅ Service: Running\n"
        "🔒 TLS: Enabled\n"
        "🚀 Protocol: VLESS"
    )
    
    await update.message.reply_text(status)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "👥 Create User":
        await create_user(update, context)
    elif text == "📋 List Users":
        await list_users(update, context)
    elif text == "❌ Delete User":
        await delete_user(update, context)
    elif text == "📊 Server Status":
        await server_status(update, context)
    elif text == "ℹ️ Help":
        await help_command(update, context)
    elif context.user_data.get('waiting_for') == 'email':
        await handle_email(update, context)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("create", create_user))
    application.add_handler(CommandHandler("list", list_users))
    application.add_handler(CommandHandler("delete", delete_user))
    application.add_handler(CommandHandler("status", server_status))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()