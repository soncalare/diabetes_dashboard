#Flask: para crear el backend del dashboard
#pandas: para procesar y analizar datos del CVS
#ploty.express: para generar graficos interactivos
#os: para manejar rutas y archivos en el sistema operativo
#werkzeug.utils: para gestionar nombres seguros al guardar archivos
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from werkzeug.utils import secure_filename

app = Flask(__name__)  #inicializa la aplicacion Flask
UPLOAD_FOLDER = 'uploads'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER   #Carpeta para almacenar archivos subidos   
ALLOWED_EXTENSIONS = {'csv'}    #se define tipo de archivos permitidos
# Funcion para asegurarnos de que solo se procesen archivos CVS
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#Muestra el formulario para subir un archivo y maneja la subida
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':   
        if 'file' not in request.files:   #Recupera el archivo subido por el usuario
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)   #garantiza que el nombre del archivo no cause problemas de seguridad
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('dashboard', filename=filename))   #redirige al usuario al dashboard despues de subir el archivo
    return render_template('index.html')
#procesa el archivo subido, genera graficos y muestra los resultados
@app.route('/dashboard/<filename>')
def dashboard(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath)  #Carga el archivo CSV en un DataFrame

    # Generar gráficos interactivos con ploty
    hist = px.histogram(df, x=df.columns[0])
    scatter = px.scatter(df, x=df.columns[0], y=df.columns[1])
    box = px.box(df, y=df.columns[0])
    correlation = df.corr()
    heatmap = px.imshow(correlation)

    return render_template(
        'dashboard.html',
        hist=hist.to_html(full_html=False),
        scatter=scatter.to_html(full_html=False),
        box=box.to_html(full_html=False),
        heatmap=heatmap.to_html(full_html=False),
        stats=df.describe().to_html(classes='table table-striped'),  #calcula estadisticas basicas como media, mediana y desviacion estandar 
    )

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  #Crea la carpeta upload y se asegura de que los archivos subidos existan
    app.run(debug=True)   #Inicia la aplicación Flask
