async def send_message_to_users(user_ids, message_text, *, bot):
    for user_id in user_ids:
        await bot.send_message(chat_id=user_id, text=message_text)
