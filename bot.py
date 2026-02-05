from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
# from ai import analyze_meal, analyze_meal_lmstudio, reset_chroma_db
# from database import log_meal, get_daily_stats, reset_sql_db
from ai import analyze_meal

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo_file = await update.message.photo[-1].get_file()
    path = f"./data/{photo_file.file_id}.jpg"
    await photo_file.download_to_drive(path)

    status_msg = await update.message.reply_text("🍳 Analyzing your meal...")

    # Get both the data and the diagnostic verbose string
    # result, diagnostics = analyze_meal(path, user_id)
    result, diagnostics = analyze_meal(path, user_id)

    # log_meal(user_id, result)

    reply = (f"✅ Found: {result['food_name']}\n"
             f"🔥 Calories: {result['calories']} kcal\n"
             f"💪 Protein: {result['protein']}g\n"
             f"🍞 Carbs: {result['carbs']}g\n"
             f"🥑 Fats: {result['fats']}g\n"
             f"debug lines: \n\n {diagnostics}")

    await update.message.reply_text(reply)

# async def automated_daily_summary(context):
#     user_ids = ["1053186437"]
#     app = context.application

#     for uid in user_ids:
#         stats = get_daily_stats(uid)
#         if stats[0]:
#             goal = 2000
#             progress = get_progress_bar(stats[0], goal)
#             message = (
#                 f"📊 *Daily Report*\n"
#                 f"Calories: {stats[0]} / {goal} kcal\n"
#                 f"{progress}\n\n"
#                 f"💪 Protein: {stats[1]}g\n"
#                 f"🍞 Carbs: {stats[2]}g\n"
#                 f"🥑 Fats: {stats[3]}g"
#             )
#             await app.bot.send_message(
#                 chat_id=uid,
#                 text=message,
#                 parse_mode='Markdown'
#             )

# async def summary_command(update, context):
#     user_id = update.effective_user.id
#     stats = get_daily_stats(user_id)
#     if stats[0]:
#         goal = 2000
#         progress = get_progress_bar(stats[0], goal)
#         message = (
#             f"📊 *Daily Report*\n"
#             f"Calories: {stats[0]} / {goal} kcal\n"
#             f"{progress}\n\n"
#             f"💪 Protein: {stats[1]}g\n"
#             f"🍞 Carbs: {stats[2]}g\n"
#             f"🥑 Fats: {stats[3]}g"
#         )
#         await app.bot.send_message(
#             chat_id=user_id,
#             text=message,
#             parse_mode='Markdown'
#         )

# def get_progress_bar(current, goal):
#     percentage = min(current / goal, 1.0)
#     filled_length = int(10 * percentage)
#     bar = "🟩" * filled_length + "⬜️" * (10 - filled_length)
#     return f"{bar} {int(percentage * 100)}%"

# async def delete_last_command(update, context):
#     user_id = update.effective_user.id
#     if user_id in last_uploads:
#         delete_last_sql_entry(user_id)
#         delete_last_chroma_entry(user_id, last_uploads[user_id])
#         await update.message.reply_text("🗑️ Last entry removed from SQL and ChromaDB.")
#         del last_uploads[user_id]
#     else:
#         await update.message.reply_text("❌ No recent entry found to delete.")

# async def reset_command(update, context):
#     # Safety check: You might want to restrict this to your own user_id!
#     reset_sql_db()
#     reset_chroma_db()
#     await update.message.reply_text("💥 Database fully reset. Fresh start!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    job_queue = app.job_queue

    # Schedule the 9 PM job (Cron-style)
    # 21:00:00 every day
    # from datetime import time
    # job_queue.run_daily(automated_daily_summary, time(hour=21, minute=0))
    # job_queue.run_repeating(automated_daily_summary, interval=60, first=5)

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    # app.add_handler(CommandHandler("summary", summary_command))
    # app.add_handler(CommandHandler("delete", delete_last_command))
    # app.add_handler(CommandHandler("reset", reset_command))
    app.run_polling()
