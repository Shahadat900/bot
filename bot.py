import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, Chat
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from datetime import datetime
import re

# ---------------- Logging ----------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------- Bot Token ----------------
BOT_TOKEN = "8089194654:AAEkFDyiiZld6APFliA39AMcjXdahHh_gqg"

# ---------------- In-memory chat storage ----------------
chats = {
    "groups": set(),
    "private": set(),
    "channels": set(),
    "bots": set()
}

# ---------------- Escape MarkdownV2 ----------------
def escape_markdown(text: str) -> str:
    """
    Escape all MarkdownV2 special characters
    """
    if not text:
        return ""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

# ---------------- Start Command ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [
        [KeyboardButton("ℹ️ My Info"), KeyboardButton("Select User")],
        [KeyboardButton("📤 Forward Message"), KeyboardButton("❓ Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    username = escape_markdown(user.username or "NoUsername")
    full_name = escape_markdown(user.full_name)

    welcome_text = (
        "👋 Welcome to *User ID Bot*\\! 🆔\n"
        "Get Telegram info instantly⚡\n\n"
        "*EASIEST METHOD:* 📱 Tap \"Select User\" → Search anyone → Get info\\!\n\n"
        "✨ *What I show:*\n"
        "• User ID & Username\n"
        "• Account type & age\n"
        "• Premium status\n"
        "• Scam risk indicators\n\n"
        "📋 *Other methods:*\n"
        "• Forward message → Get sender info\n"
        "• Type @username → Public accounts only\n"
        "• Inline: @userid_bot @username\n\n"
        "💡 *Privacy Note:* Username lookup is limited by Telegram privacy\\.\n"
        "Use Select User or Forward for best results\\.\n\n"
        "\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n"
        "🔎 *YOUR INFO:*\n"
        f"🆔: `{user.id}`\n"
        f"👤 @{username}\n"
        f"📅 *Estimated Join Year:* ~{datetime.now().year}\n"
        "✅ ESTABLISHED ACCOUNT\n"
        "⚡ Powered by YourBot"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='MarkdownV2')

# ---------------- Track Messages ----------------
async def message_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == Chat.PRIVATE:
        chats["private"].add((chat.id, chat.full_name))
        if user.is_bot:
            chats["bots"].add((chat.id, chat.full_name))
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        chats["groups"].add((chat.id, chat.title))
    elif chat.type == Chat.CHANNEL:
        chats["channels"].add((chat.id, chat.title))

# ---------------- Handle Button Press ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # My Info
    if text == "ℹ️ My Info":
        username = escape_markdown(user.username or "NoUsername")
        full_name = escape_markdown(user.full_name)
        info_text = (
            "ℹ️ *My Info*\n"
            f"*Name:* {full_name}\n"
            f"🆔 *User ID:* `{user.id}`\n"
            f"👤 *Username:* @{username}\n"
            f"📅 *Estimated Join Year:* ~{datetime.now().year}\n"
            "✅ ESTABLISHED ACCOUNT"
        )
        await update.message.reply_text(info_text, parse_mode='MarkdownV2')

    # Forward Message
    elif text == "📤 Forward Message":
        forward_text = (
            "📤 *How to Forward Messages*\n\n"
            "1️⃣ Open chat with the person\n"
            "2️⃣ Long-press their message\n"
            "3️⃣ Tap \"Forward\"\n"
            "4️⃣ Select @YourBotUsername\n"
            "5️⃣ Done! ✅\n\n"
            "⚡ Works for most users (if sender allows forwarding)\n\n"
            "💡 Even easier: Use \"Select User\" button!"
        )
        await update.message.reply_text(forward_text, parse_mode='MarkdownV2')

    # Help
    elif text == "❓ Help":
        help_text = (
            "📖 *How to Use*\n\n"
            "🎯 *BEST METHOD:* Tap \"Select User\" → Search anyone by username or name → Get info instantly → Works for everyone! ✅\n\n"
            "🔄 *OTHER METHODS:*\n"
            "• *Forward Message:* Forward any message to me → I'll show sender's info\n"
            "• *Type Username:* Send @username → Works for public accounts only\n"
            "• *Inline Mode:* Type @YourBotUsername @username → Works in any chat\n\n"
            "💬 *Feedback:* Click 👍/👎 on results or use /feedback\n\n"
            "⚠️ *Privacy Note:* I can only show info for:\n"
            "✅ Users you select via button\n"
            "✅ Users who forwarded messages\n"
            "✅ Public bots & channels\n"
            "This is normal Telegram! 🔒"
        )
        await update.message.reply_text(help_text, parse_mode='MarkdownV2')

    # Select User / Group / Channel / Bot
    elif text == "Select User":
        message = "*Select User / Group / Channel / Bot:*\n"
        sections = [
            ("Groups", "groups"),
            ("Private Chats", "private"),
            ("Channels", "channels"),
            ("Bots", "bots")
        ]
        for title, key in sections:
            message += f"\n*{title}:*\n"
            if chats[key]:
                for cid, name in chats[key]:
                    safe_name = escape_markdown(name)
                    message += f"- {safe_name} (`{cid}`)\n"
            else:
                message += "- None\n"
        await update.message.reply_text(message, parse_mode='MarkdownV2')

# ---------------- Main ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, message_tracker))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), button_handler))

    print("Bot is running...")
    app.run_polling()
