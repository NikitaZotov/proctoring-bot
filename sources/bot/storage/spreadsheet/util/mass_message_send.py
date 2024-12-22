async def send_message_to_users(user_ids, message_text):
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=message_text)
            print(f"Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
