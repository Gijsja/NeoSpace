from app import create_app
from sockets import socketio

app = create_app()

if __name__ == '__main__':
    print("Starting NeoSpace with SocketIO...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
