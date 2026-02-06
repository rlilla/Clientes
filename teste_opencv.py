import cv2
from collections import deque
from flask import Flask, render_template, url_for, request,session, redirect
import threading
import datetime
import os
import json

enderecoCam = 0
buffer = deque(maxlen=30*30)
saving = False
app=Flask("__name__")
frame_width = ""
frame_height = ""
app.secret_key='TESTE'

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=5)

def salvar():
    global saving
    global frame_width, frame_height
    data = datetime.datetime.now()
    nomeArquivo = f"{data.date().day:02d}_{data.date().month:02d}_{data.date().year}_{data.time().hour:02d}_{data.time().minute:02d}_{data.time().second:02d}.mp4"
    print(saving)
    #fourcc = cv2.VideoWriter_fourcc(*"XVID")
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    out = cv2.VideoWriter(f'./static/{nomeArquivo}',fourcc,30.0,(frame_width, frame_height))
    for fr in buffer:
        out.write(fr)
    out.release()
def t1():
    global saving
    global enderecoCam
    global frame_height, frame_width
    print(enderecoCam)
    camera = cv2.VideoCapture(int(enderecoCam))   
    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))     
    while True:
        ret, frame = camera.read()
        cv2.imshow("TESTE",frame)
        if not saving:
            buffer.append(frame.copy())
        key = cv2.waitKey(1)

        if key == ord('q'):
            break

        if key == ord('s'):
            salvar()
    camera.release()
    cv2.destroyAllWindows()

@app.route('/teste')
def teste():
    global saving
    saving = True
    salvar()
    saving = False
    return "OK"
@app.route('/iniciar')
def iniciar():
    global enderecoCam
    enderecoCam = request.args.get("ip")
    t = threading.Thread(target=t1)
    t.start()
    t.join()
    return "OK"
@app.route('/')
def index():
    arquivos = os.listdir('./static')
    print(arquivos)
    if 'logado' in session.keys():
        if session['logado']:
            return render_template('index.html',arquivos=arquivos)
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        usuario = request.form['txtUser']
        senha = request.form['txtPwd']
        if senha=='1234':
            session['logado'] = True
            return redirect('/')
        else:
            session['logado'] = False
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logado'] = False
    session.pop('logado')
    return redirect('/login')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')
@app.route('/salvaCadastro',methods=['POST','GET'])
def salvaCadastro():
    dados = request.json
    print(dados)
    return "OK"

@app.route('/contas')
def contas():
    pessoas = [{'nome':'Joao','idade':52}, {'nome':'Pedro','idade':34}]
    return render_template('contas.html',pessoas=pessoas)

app.run('0.0.0.0', port=8080, debug=True)


cv2.destroyAllWindows()

