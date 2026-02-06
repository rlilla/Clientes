import cv2
import base64
import numpy as np
from flask import Flask, render_template 
from flask_socketio import SocketIO, emit 
from ultralytics import YOLO 
import io 
from PIL import Image
import collections
import time

# Configuração do Flask e SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
model = YOLO('yolov8n.pt')

buffer_video = collections.deque(maxlen=900)

saving = False
@app.route('/')
def index():
    return render_template('teste.html')

@app.route('/salvar')
def salvar():
    global buffer_video, saving
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    out = cv2.VideoWriter(f'./static/teste.mp4',fourcc,30.0,(640, 480))
    saving = True
    print(len(buffer_video))
    for fr in buffer_video:
        out.write(fr)
    out.release()
    saving = False
    return "OK"

def process_frame(image_data):
    global buffer_video, saving
    try:
        header, encoded = image_data.split(",", 1) 
        data = base64.b64decode(encoded)
        np_arr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            return None
        
        if not saving:
            buffer_video.append(frame.copy())
        #results = model(frame, conf=0.4)

        #annotated_frame = results[0].plot()

        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{jpg_as_text}"

    except Exception as e:
        print(f"Erro no processamento: {e}")
        return None

@socketio.on('video_frame')
def handle_video_frame(data):
    processed_frame = process_frame(data)
    if processed_frame:
        emit('response_back', processed_frame)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
