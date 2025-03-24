
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# توکن ربات
TOKEN = "7994169968:AAFTJYFwpRtORUW0bAkGWGCG2cdQ6Khp4Y4"

# بارگذاری لیست محصولات
with open("product_list.txt", encoding="utf-8") as f:
    PRODUCT_LIST = [line.strip() for line in f.readlines()]

# راه‌انداز لاگ
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! نام کامل محصول موردنظر رو بفرست تا قیمت‌ها از ترب برات بیارم.")

def search_torob(product_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://torob.com/search/?q={requests.utils.quote(product_name)}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    product_link_tag = soup.select_one("a.product-item")
    if not product_link_tag:
        return "محصولی در ترب پیدا نشد."

    product_url = "https://torob.com" + product_link_tag["href"]

    res = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    shops = soup.select(".product-seller-row")

    result = f"**نتایج برای:** {product_name}

"
    for shop in shops:
        seller = shop.select_one(".product-seller-name span")
        price = shop.select_one(".product-seller-price span")
        city = shop.select_one(".product-seller-location")

        if seller and price:
            result += f"فروشنده: {seller.text.strip()}
"
            result += f"قیمت: {price.text.strip()}
"
            if city:
                result += f"شهر: {city.text.strip()}
"
            result += "
"

    result += f"لینک محصول در ترب:
{product_url}"
    return result

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text in PRODUCT_LIST:
        await update.message.reply_text("در حال جستجوی قیمت‌ها در ترب...")
        result = search_torob(text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("محصول پیدا نشد یا هنوز داخل لیست نیست.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
