from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

# Fungsi untuk mengambil frame dari webcam
def get_frame():
    camera = cv2.VideoCapture(0)  # Mengakses webcam (index 0)
    while True:
        success, frame = camera.read()  # Membaca frame dari webcam
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Menghasilkan frame sebagai respons

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
    print('Client connected')
    emit('start_streaming')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@socketio.on('request_frame')
def request_frame():
    emit('frame', next(get_frame()))

if __name__ == '__main__':
    socketio.run(app)
