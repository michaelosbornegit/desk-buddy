class InternalSocketio:
    __socketio = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(InternalSocketio, cls).__new__(cls)
        return cls.instance

    def init(self, socketio):
        self.__socketio = socketio

        @socketio.on("connect")
        def handle_connect():
            print("Client connected")

    def get_socketio(self):
        return self.__socketio


instance = InternalSocketio()
