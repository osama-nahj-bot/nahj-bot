import os
import asyncio
import gspread
import nest_asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler,
                          MessageHandler, filters, ConversationHandler)
from oauth2client.service_account import ServiceAccountCredentials

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS =ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", scope)
client = gspread.authorize(CREDS)

# اسم الشيت وصفحتين للذكور والإناث
SHEET_NAME = "NahjAcademySheet"
SHEET_MALE = "الذكور"
SHEET_FEMALE = "الاناث"
sheet_male = client.open(SHEET_NAME).worksheet(SHEET_MALE)
sheet_female = client.open(SHEET_NAME).worksheet(SHEET_FEMALE)

# تعريف المراحل
NAME, AGE, GOAL, COUNTRY, GENDER = range(5)

# دالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"""🎉 أهلاً وسهلاً بك في *أكاديمية نهج* لتحفيظ وتعليم القرآن الكريم عن بُعد، {user.first_name}!

📌 *قبل أن تبدأ التسجيل، يُرجى اتباع الخطوات التالية:*

1. 🔹 اضغط على زر *من نحن* لتتعرف على رؤيتنا ورسالتنا، وطريقة التعليم والمتابعة.
2. ▶️ شاهد الفيديو الترحيبي القصير لتأخذ فكرة واضحة عن البرنامج والمستويات والخدمات المقدمة.
3. 📝 بعد ذلك، توجه إلى زر *التسجيل* لإدخال معلوماتك والالتحاق بالأكاديمية.

📚 *نسأل الله أن يبارك لك في هذا السعي المبارك، وأن يجعل القرآن الكريم ربيع قلبك ونور صدرك 🌿*""",
        parse_mode='Markdown'
    )
    keyboard = [[KeyboardButton("من نحن")], [KeyboardButton("التسجيل")]]
    await update.message.reply_text("اختر من القائمة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# من نحن
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """📖 *عن أكاديمية نهج:*

نحن أكاديمية متخصصة في تحفيظ وتعليم القرآن الكريم عن بُعد، بإشراف نخبة من المعلمين والمعلمات.

🔹 نُقدّم برنامجًا متكاملًا يشمل:
- حلقات فردية وجماعية
- متابعة دورية وتقييم شامل
- مستويات متعددة تناسب الجميع

🎥 شاهد الفيديو التعريفي التالي لتفهم أكثر عن طريقة العمل 👇
""",
        parse_mode='Markdown'
    )

    # إرسال الفيديو باستخدام file_id
    await update.message.reply_video(
        video="BAACAgQAAxkBAANuaGP96sXyixrepVEce63yIUgLgFUAAhYXAAJB9yFTByDjFUfgZMI2BA",
        caption="🎞 *الفيديو التعريفي لأكاديمية نهج*",
        parse_mode="Markdown"
    )

    # إرسال زر القناة الرسمية
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 القناة الرسمية", url="https://t.me/+aE8i5fu47nQxOTZk")]
    ])
    await update.message.reply_text("⬅️ انضم إلى قناتنا الرسمية:", reply_markup=keyboard)


# بدء التسجيل
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

    # عرض خيارات إضافية بعد التسجيل
    keyboard = [
        [KeyboardButton("من نحن")],
        [KeyboardButton("التسجيل")]
    ]
    await update.message.reply_text("⬅️ يمكنك الآن العودة للتعرف أكثر على الأكاديمية أو تسجيل شخص آخر.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # زر الانضمام للقناة الرسمية (Inline)
    channel_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 القناة الرسمية", url="https://t.me/+aE8i5fu47nQxOTZk")]
    ])
    await update.message.reply_text("⬅️ انضم إلى قناتنا الرسمية:", reply_markup=channel_button)

    return ConversationHandler.END

# إلغاء
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# تشغيل البوت
async def main():
    app = ApplicationBuilder().token(os.environ['TOKEN']).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^التسجيل$"), register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^من نحن$"), about))
    app.add_handler(conv_handler)

    print("🤖 البوت يعمل الآن...")
    await app.run_polling()

# تشغيل متوافق مع Replit
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
