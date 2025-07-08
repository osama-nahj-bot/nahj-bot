import os
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import nest_asyncio

# تفعيل التوافق مع asyncio في Render
nest_asyncio.apply()

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", SCOPE)
client = gspread.authorize(CREDS)

SHEET_NAME = "NahjAcademySheet"
SHEET_MALE = "الذكور"
SHEET_FEMALE = "الاناث"

sheet_male = client.open(SHEET_NAME).worksheet(SHEET_MALE)
sheet_female = client.open(SHEET_NAME).worksheet(SHEET_FEMALE)

# الحالات
NAME, AGE, GOAL, COUNTRY, GENDER = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"""🎉 أهلاً وسهلاً بك في أكاديمية نهج، {user.first_name}!

📌 قبل أن تبدأ، يُرجى الضغط على "من نحن" لمعلومات شاملة أو على "التسجيل" للبدء مباشرة.
""", parse_mode='Markdown')
    keyboard = [[KeyboardButton("من نحن")], [KeyboardButton("التسجيل")]]
    await update.message.reply_text("اختر من القائمة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """📖 عن أكاديمية نهج:

نحن أكاديمية متخصصة في تحفيظ وتعليم القرآن الكريم عن بُعد.

🎥 شاهد الفيديو التالي 👇""",
        parse_mode='Markdown'
    )
    await update.message.reply_video(
        video="BAACAgQAAxkBAANuaGP96sXyixrepVEce63yIUgLgFUAAhYXAAJB9yFTByDjFUfgZMI2BA",
        caption="🎞 الفيديو التعريفي",
        parse_mode="Markdown"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 القناة الرسمية", url="https://t.me/+aE8i5fu47nQxOTZk")]
    ])
    await update.message.reply_text("⬅️ انضم إلى قناتنا:", reply_markup=keyboard)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 ما اسمك الكامل؟", reply_markup=ReplyKeyboardRemove())
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📅 كم عمرك؟")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text("🎯 ما هدفك من التسجيل؟")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text
    await update.message.reply_text("🌍 من أي دولة أنت؟")
    return COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["country"] = update.message.text
    keyboard = [[KeyboardButton("ذَكر"), KeyboardButton("أنثى")]]
    await update.message.reply_text("⚧️ ما جنسك؟", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text
    data = context.user_data
    row = [data["name"], data["age"], data["goal"], data["country"], gender]
    if gender == "ذَكر":
        sheet_male.append_row(row)
    else:
        sheet_female.append_row(row)

    await update.message.reply_text("✅ تم التسجيل بنجاح!", reply_markup=ReplyKeyboardRemove())
    keyboard = [[KeyboardButton("من نحن")], [KeyboardButton("التسجيل")]]
    await update.message.reply_text("⬅️ يمكنك الآن العودة للتعرف على الأكاديمية أو تسجيل شخص آخر.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def main():
    app = ApplicationBuilder().token(os.environ["TOKEN"]).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^التسجيل$"), register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^من نحن$"), about))
    app.add_handler(conv_handler)

    print("✅ البوت يعمل الآن على Render...")
    await app.run_polling()

if _name_ == "_main_":
    asyncio.run(main())
