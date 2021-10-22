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
