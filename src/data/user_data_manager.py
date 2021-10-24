"""
"""


class UserDataManager:
    # keys
    (
        ATTRIBUTES,
        CURRENT_ATTRIBUTE,
        USER_ID,
        USER_ALIAS,
        CHAT_ID,
        USERNAME,
        REPEATED_START,
        ERROR
    ) = map(chr, range(10, 18))

    def update_callback(self, user_data, value: bool):
        user_data[self.REPEATED_START] = value

    def is_updated_callback(self, user_data):
        return user_data.get(self.REPEATED_START)

    def is_error_occurred(self, user_data):
        return user_data.get(self.ERROR)

    def get_error(self, user_data):
        error = user_data[self.ERROR]
        del user_data[self.ERROR]
        return error

    def set_error(self, user_data, value):
        user_data[self.ERROR] = value

    def set_user_alias(self, user_data, value):
        user_data[self.USER_ALIAS] = value

    def get_user_alias(self, user_data):
        return user_data.get(self.USER_ALIAS)

    def set_user_id(self, user_data, user_id: int):
        user_data[self.USER_ID] = str(user_id)

    def get_user_id(self, user_data):
        return user_data.get(self.USER_ID)

    def set_chat_id(self, user_data, chat_id: int):
        user_data[self.CHAT_ID] = str(chat_id)

    def get_chat_id(self, user_data):
        return user_data.get(self.CHAT_ID)

    def set_username(self, user_data, id_name: str):
        user_data[self.USERNAME] = id_name

    def get_username(self, user_data):
        return user_data.get(self.USERNAME)

    def set_user_attrs(self, user_data, other):
        user_data[self.ATTRIBUTES] = other

    def get_user_attrs(self, user_data):
        return user_data.get(self.ATTRIBUTES)

    def set_user(self, user_data, data):
        user_data[self.get_user_id(user_data)] = data

    def set_cur_user_attr_key(self, user_data, data):
        user_data[self.CURRENT_ATTRIBUTE] = data

    def get_cur_user_attr_key(self, user_data):
        return user_data.get(self.CURRENT_ATTRIBUTE)

    def set_cur_user_attr(self, user_data, data):
        user_data[self.ATTRIBUTES][self.get_cur_user_attr_key(user_data)] = data

    def get_user_attrs_by_id(self, user_data):
        return user_data.get(self.get_user_id(user_data))

    def get_user_attrs_by_id_name(self, user_data, id_name):
        return user_data.get(user_data.get(id_name))
