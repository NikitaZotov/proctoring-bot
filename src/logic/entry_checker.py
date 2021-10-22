class EntryChecker:
    @staticmethod
    def is_name_correct(name: str) -> bool:
        words = name.split()
        if len(words) != 3:
            return False

        for word in words:
            if any(not letter.isalpha() for letter in word):
                return False

        return True

    @staticmethod
    def to_minutes_str_format(minutes: int) -> str:
        if minutes % 10 == 1 and minutes % 100 != 11:
            return f'{minutes} минуты'
        else:
            return f'{minutes} минут'
