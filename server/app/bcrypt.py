class GlobalBcrypt:
    __bcrypt = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(GlobalBcrypt, cls).__new__(cls)
        return cls.instance

    def init(self, bcrypt):
        self.__bcrypt = bcrypt

    def generate_hash(self, value):
        return self.__bcrypt.generate_password_hash(value).decode("utf-8")

    def check_hash(self, value, hashed_value):
        return self.__bcrypt.check_password_hash(hashed_value, value)


instance = GlobalBcrypt()
