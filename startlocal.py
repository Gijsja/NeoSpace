from app import create_app
from sockets import socketio

app = create_app()

if __name__ == '__main__':
    print("Starting NeoSpace with SocketIO...")
    socketio.sleep(0.1) # Yield to event loop
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, use_reloader=False)
