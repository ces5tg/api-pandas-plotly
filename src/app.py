from flask import Flask, jsonify, request, send_file
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go

import os
import pandas as pd
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_form():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Aquí puedes procesar el archivo si es necesario
            return upload()

    return '''
    <!doctype html>
    <title>Subir archivo CSV</title>
    <h1>Subir archivo CSV</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        # Cargar el archivo CSV en un DataFrame de pandas
        ratings = pd.read_csv(file)

        # Crear la gráfica Plotly
        data = ratings['rating'].value_counts().sort_index(ascending=False)

        trace = go.Bar(
            x=data.index,
            text=['{:.1f} %'.format(val) for val in (data.values / ratings.shape[0] * 100)],
            textposition='auto',
            textfont=dict(color='#000000'),
            y=data.values,
        )

        # Crear el diseño del gráfico
        layout = dict(title='Distribution Of {} ratings'.format(ratings.shape[0]),
                    xaxis=dict(title='Rating'),
                    yaxis=dict(title='Count'))

        # Convertir la figura de Plotly en una imagen PNG
        fig = go.Figure(data=[trace], layout=layout)

        # Verificar si la carpeta existe, y si no, crearla
        if not os.path.exists("imagenes/"):
            os.makedirs("imagenes/")

        # Guardar la figura como imagen
        img_path = os.path.join("imagenes/", 'ratings.png')
        fig.write_image(img_path)

        # Leer el contenido binario de la imagen
        with open(img_path, 'rb') as img_file:
            img_binary = img_file.read()

        # Retornar el contenido binario de la imagen y su tipo MIME
        return send_file(io.BytesIO(img_binary), mimetype='image/png')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)



