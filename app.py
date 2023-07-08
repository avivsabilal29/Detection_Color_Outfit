from flask import Flask, Response, render_template
import cv2
import numpy as np
import threading
import os
import playsound


app = Flask(__name__)

# URL video streaming
# url = 'http://192.168.140.164:8080/video'
url = 'http://192.168.1.8:8080/video'

# Buat objek VideoCapture menggunakan URL
cap = cv2.VideoCapture(url)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

# Daftar warna yang akan dideteksi
colors = {
    "Putih": {"lower": np.array([0, 0, 150]), "upper": np.array([180, 20, 255])},
    "Hitam": {"lower": np.array([0, 0, 0]), "upper": np.array([180, 255, 50])},
    "Merah": {"lower": np.array([0, 100, 100]), "upper": np.array([10, 255, 255])},
    "Kuning": {"lower": np.array([25, 100, 100]), "upper": np.array([35, 255, 255])},
    "Hijau": {"lower": np.array([35, 100, 100]), "upper": np.array([85, 255, 255])},
    "Biru": {"lower": np.array([85, 100, 100]), "upper": np.array([125, 255, 255])},
    "Orange": {"lower": np.array([10, 100, 100]), "upper": np.array([25, 255, 255])},
    "Coklat": {"lower": np.array([10, 50, 50]), "upper": np.array([20, 255, 255])},
    "Pink tua": {"lower": np.array([145, 100, 100]), "upper": np.array([155, 255, 255])},
    "Pink muda": {"lower": np.array([155, 100, 100]), "upper": np.array([165, 255, 255])},
    "Pink": {"lower": np.array([165, 100, 100]), "upper": np.array([175, 255, 255])},
    "Merah maroon": {"lower": np.array([175, 100, 100]), "upper": np.array([180, 255, 255])},
    "Abu-abu": {"lower": np.array([0, 0, 100]), "upper": np.array([180, 20, 200])},
    "Abu-abu tua": {"lower": np.array([0, 0, 50]), "upper": np.array([180, 20, 100])},
    "Abu-abu muda": {"lower": np.array([0, 0, 150]), "upper": np.array([180, 20, 200])},
    "Merah tua": {"lower": np.array([0, 100, 100]), "upper": np.array([10, 255, 255])},
    "Kuning tua": {"lower": np.array([25, 100, 100]), "upper": np.array([35, 255, 255])},
    "Hijau tua": {"lower": np.array([35, 100, 100]), "upper": np.array([85, 255, 255])},
    "Ungu tua": {"lower": np.array([125, 100, 100]), "upper": np.array([145, 255, 255])},
    "Denim": {"lower": np.array([85, 100, 100]), "upper": np.array([125, 255, 255])},
    "Cokelat Tua": {"lower": np.array([10, 50, 50]), "upper": np.array([20, 255, 255])},
    "Cokelat Muda": {"lower": np.array([20, 50, 50]), "upper": np.array([30, 255, 255])},
    "Biru Tua": {"lower": np.array([105, 100, 100]), "upper": np.array([125, 255, 255])},
    "Biru muda": {"lower": np.array([125, 100, 100]), "upper": np.array([135, 255, 255])},
    "Biru Dongker": {"lower": np.array([135, 100, 100]), "upper": np.array([145, 255, 255])},
    "Krem": {"lower": np.array([0, 20, 150]), "upper": np.array([180, 100, 255])},
    "Emas": {"lower": np.array([20, 100, 100]), "upper": np.array([35, 255, 255])},
    "Hijau Sage": {"lower": np.array([45, 100, 100]), "upper": np.array([75, 255, 255])},
    "Hijau Army": {"lower": np.array([75, 100, 100]), "upper": np.array([95, 255, 255])}
}


# Variabel global untuk menyimpan hasil pembacaan warna
detected_color = ""

# Objek lock untuk sinkronisasi akses ke variabel detected_color
color_lock = threading.Lock()

def generate_frames():
    global detected_color
    while True:
        _, frame = cap.read()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width, _ = frame.shape

        cx = int(width / 2)
        cy = int(height / 2)

        # Pick pixel value
        pixel_center = hsv_frame[cy, cx]
        h, s, v = int(pixel_center[0]), int(pixel_center[1]), int(pixel_center[2])

        color = "Tidak Terdeteksi"
        for color_name, color_range in colors.items():
            lower_range = color_range["lower"]
            upper_range = color_range["upper"]
            if lower_range[0] <= h <= upper_range[0] and lower_range[1] <= s <= upper_range[1] and lower_range[2] <= v <= upper_range[2]:
                color = color_name
                break

        pixel_center_bgr = frame[cy, cx]
        b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])

        cv2.rectangle(frame, (cx - 440, 20), (cx + 270, 125), (255, 255, 255), -1)
        cv2.putText(frame, color, (cx - 290, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (b, g, r), 5)
        cv2.circle(frame, (cx, cy), 5, (255, 202, 12), 3)
        with color_lock:
            detected_color = color

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def play_sound():
    global detected_color
    while True:
        with color_lock:
            color2 = detected_color

        # Menentukan jalur folder sound
        sound_folder = os.path.join(os.path.dirname(__file__), "sound")

        # Menentukan file suara yang akan diputar berdasarkan warna yang terdeteksi
        sound_file = ""
        if color2 == "Hitam":
            sound_file = os.path.join(sound_folder, "black.wav")
        elif color2 == "Putih":
            sound_file = os.path.join(sound_folder, "white.wav")
        elif color2 == "Merah":
            sound_file = os.path.join(sound_folder, "red.wav")
        elif color2 == "Kuning":
            sound_file = os.path.join(sound_folder, "yellow.wav")
        elif color2 == "Hijau":
            sound_file = os.path.join(sound_folder, "green.wav")
        elif color2 == "Biru":
            sound_file = os.path.join(sound_folder, "blue.wav")
        elif color2 == "Coklat":
            sound_file = os.path.join(sound_folder, "brown.wav")
        elif color2 == "Pink tua":
            sound_file = os.path.join(sound_folder, "dark_pink.wav")
        elif color2 == "Pink":
            sound_file = os.path.join(sound_folder, "pink.wav")
        elif color2 == "Pink muda":
            sound_file = os.path.join(sound_folder, "light_pink.wav")
        elif color2 == "Merah maroon":
            sound_file = os.path.join(sound_folder, "maroon.wav")
        elif color2 == "Abu-abu tua" or color2 == "Abu-abu muda":
            sound_file = os.path.join(sound_folder, "gray.wav")
        elif color2 == "Merah tua" or color2 == "Kuning tua":
            sound_file = os.path.join(sound_folder, "dark_red_yellow.wav")
        elif color2 == "Krem":
            sound_file = os.path.join(sound_folder, "cream.wav")
        else:
            # Jika warna tidak dikenali, tidak ada file suara yang diputar
            continue

        # Memainkan suara menggunakan playsound
        playsound.playsound(sound_file)

# Membuat thread pertama untuk pembacaan warna
color_thread = threading.Thread(target=generate_frames)

# Membuat thread kedua untuk pemutaran suara
sound_thread = threading.Thread(target=play_sound)

# Menjalankan thread pertama dan kedua secara bersamaan
color_thread.start()
sound_thread.start()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    # Menunggu hingga kedua thread selesai
    color_thread.join()
    sound_thread.join()
    cap.release()
    cv2.destroyAllWindows()


