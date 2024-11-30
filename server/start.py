import app.app as app
import app.socketio_instance as socketio_instance
from config import Config

# import things so they write to requirements.txt

if __name__ == "__main__":
    created_app = app.create_app()
    socketio_instance.instance.get_socketio().run(
        created_app, host="0.0.0.0", port=Config.PORT, debug=True, use_reloader=False
    )
