import json
import random
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "ضع هنا التوكن بتاعك"

ADMIN_ID = 1823594728
GROUP_ID = -1002268255069

def load_data():
    with open("keys.json", "r") as f:
        keys = json.load(f)
    with open("balances.json", "r") as f:
        balances = json.load(f)
    with open("prices.json", "r") as f:
        prices = json.load(f)
    return keys, balances, prices

def save_data(keys, balances):
    with open("keys.json", "w") as f:
        json.dump(keys, f)
    with open("balances.json", "w") as f:
        json.dump(balances, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balances = load_data()[1]
    balances.setdefault(str(user.id), 0)
    save_data(load_data()[0], balances)

    lang = user.language_code
    if lang == "ar":
        msg = f"""مرحبا {user.first_name} ⚡
لتكون موزعاً تواصل مع المالك 🔥
- @AbdullahNaiem

قائمة الأسعار 🔑
اسبوع لعب تلقائي : 7$
اسبوع لعب ودخول تلقائي : 8.5$

شهر لعب تلقائي : 17$
شهر لعب و دخول تلقائي 20$
"""
    else:
        msg = f"""Welcome {user.first_name} ⚡
To become a distributor contact the owner 🔥
- @AbdullahNaiem

Prices 🔑
Auto Play Weekly: $7
Auto Play + Login Weekly: $8.5

Auto Play Monthly: $17
Auto Play + Login Monthly: $20
"""

    await update.message.reply_photo(photo=open("welcome.jpg", "rb"), caption=msg)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balances = load_data()[1]
    balance = balances.get(str(update.effective_user.id), 0)
    await update.message.reply_text(f"رصيدك الحالي: {balance} $")

async def addbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        target_id = context.args[0]
        amount = float(context.args[1])
    except:
        await update.message.reply_text("الاستخدام: /addbalance user_id المبلغ")
        return

    keys, balances, prices = load_data()
    balances[target_id] = balances.get(target_id, 0) + amount
    save_data(keys, balances)
    await update.message.reply_text("تم الإيداع بنجاح.")
    await context.bot.send_message(chat_id=target_id, text=f"تم إضافة {amount}$ بواسطة مالك البوت 🎱❕")

async def normal7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_purchase(update, context, "normal7")

async def normal30(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_purchase(update, context, "normal30")

async def aq7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_purchase(update, context, "aq7")

async def aq30(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_purchase(update, context, "aq30")

async def process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, purchase_type: str):
    keys, balances, prices = load_data()
    user_id = str(update.effective_user.id)

    price = prices.get(purchase_type)
    if balances.get(user_id, 0) < price:
        await update.message.reply_text("عذراً رصيدك غير كافي تواصل مع المشرف للإيداع - @AbdullahNaiem")
        return

    available_keys = keys.get(user_id, {}).get(purchase_type, [])
    if not available_keys:
        await update.message.reply_text("لا توجد مفاتيح متاحة حالياً.")
        return

    selected_key = available_keys.pop(0)
    keys[user_id][purchase_type] = available_keys
    balances[user_id] -= price
    save_data(keys, balances)

    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("delivery.jpg", "rb"),
                                      caption=f"""✅ Success

🔑 Key: 
{selected_key}

👤 User: 
{update.effective_user.first_name}

💰 Remaining Balance: 
{balances[user_id]} $
""")
    except:
        pass

    await context.bot.send_message(chat_id=GROUP_ID, text=f"✅ عملية شراء جديدة من {update.effective_user.username} - نوع: {purchase_type}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("addbalance", addbalance))
    app.add_handler(CommandHandler("normal7", normal7))
    app.add_handler(CommandHandler("normal30", normal30))
    app.add_handler(CommandHandler("aq7", aq7))
    app.add_handler(CommandHandler("aq30", aq30))

    app.run_polling()

if __name__ == "__main__":
    main()
