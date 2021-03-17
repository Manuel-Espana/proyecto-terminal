from flask import Flask, render_template, url_for, redirect, flash, request, send_file
from flask_mysqldb import MySQL
import datetime
import time
import pandas as pd
from matplotlib.figure import Figure
import numpy as np
import base64
import io
from matplotlib import rcParams

date = datetime.date.today()

#Ajusta automaticamente el tamaño de las graficas
rcParams.update({'figure.autolayout': True})

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bitacora'
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultados.html')
def resultados():
    return render_template('/resultados.html')

@app.route('/horaE/')
def horaE():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    #Modificacion de la hora de entrada
    data.he = pd.to_datetime(data.he)
    data.he = data.he.dt.floor('H').dt.time
    fhorae = data.groupby('he').size().reset_index(name = 'frecuencia')
    fhorae = fhorae.sort_values(by = 'frecuencia', ascending = False)
    fhorae = fhorae.head(6)
    # #Grafica las horas con mas ingresos
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.bar(fhorae.he.apply(str), fhorae.frecuencia, color = 'dodgerblue')
    ax.set_title('Horas con mas ingresos en el mes de enero')
    ax.set_ylabel('Ingresos')

    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='horaE/png')
    
@app.route('/horaS/')
def horaS():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    #Modificacion de la hora de salida
    data.hs = pd.to_datetime(data.hs)
    data.hs = data.hs.dt.floor('H').dt.time
    fhoras = data.groupby('hs').size().reset_index(name = 'frecuencia')
    fhoras = fhoras.sort_values(by = 'frecuencia', ascending = False)
    fhoras = fhoras.head(6)

    #Grafica las horas con mas salidas
    fig = Figure()
    ax2 = fig.add_subplot(111)
    ax2.bar(fhoras.hs.apply(str), fhoras.frecuencia, color = 'orangered')
    ax2.set_title('Horas con mas salidas en el mes de enero')
    ax2.set_ylabel('Salidas')

    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='horaS/png')

@app.route('/usuarios/')
def usuarios():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    #Modificacion de los usuarios
    fmotivo = data.groupby('motivo_ingreso').size().reset_index(name = 'frecuencia')

    #Grafica los usuarios
    fig = Figure()
    ax3 = fig.add_subplot(111)
    labels = fmotivo['motivo_ingreso']
    ax3.pie(fmotivo['frecuencia'], labels=labels, autopct='%1.1f%%')
    ax3.set_title('Usuarios en el mes de enero')
    ax3.axis('equal')

    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='usuarios/png')

@app.route('/depa/')
def depa():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    fdepa = data.groupby('departamento').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor y solo muestra los primeros 7
    fdepa = fdepa.sort_values(by = 'frecuencia', ascending = False)
    fdepa = fdepa.head(7)

    #Grafica los departamento
    fig = Figure()
    ax4 = fig.add_subplot(111)
    ax4.set_xticklabels(fdepa.departamento, rotation = 90, horizontalalignment = "center")
    ax4.set_title('Departamentos mas visitados en el mes de enero')
    ax4.set_ylabel('Visitas')
    ax4.bar(fdepa['departamento'], fdepa['frecuencia'], color = ('deepskyblue', 'darkorange', 'slateblue', 'gold', 'teal', 'hotpink', 'crimson'))

    #ax4.tick_params(axis='x', labelrotation = 90) 
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='depa/png')

@app.route('/fecha/')
def fecha():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    ffecha = data.groupby('fecha').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor y solo muestra los primeros 7
    ffecha = ffecha.sort_values(by = 'frecuencia', ascending = False)
    ffecha = ffecha.head(7)

    #Grafica los departamento
    fig = Figure()
    ax5 = fig.add_subplot(111)
    ax5.set_xticklabels(ffecha.fecha, rotation = 30, horizontalalignment = "center")
    ax5.set_title('Dias con mas flujo en el mes de enero')
    ax5.set_ylabel('Ingresos')
    ax5.bar(ffecha['fecha'], ffecha['frecuencia'], color = 'royalblue')

    #ax5.tick_params(axis='x', labelrotation = 90) 
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='fecha/png')

@app.route('/dia/')
def dia():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    #Conversion a tipo fecha y a dia de la semana
    data.fecha = pd.to_datetime(data.fecha)
    data.fecha = data.fecha.dt.strftime('%A')
    dia = data.groupby('fecha').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor
    dia = dia.sort_values(by = 'frecuencia', ascending = False)

    #Grafica los departamento
    fig = Figure()
    ax6 = fig.add_subplot(111)
    ax6.set_xticklabels(dia.fecha, rotation = 30, horizontalalignment = "center")
    ax6.set_title('Dias de la semana con mas flujo en el mes de enero')
    ax6.set_ylabel('Ingresos')
    ax6.bar(dia['fecha'], dia['frecuencia'], color = 'mediumseagreen')
    
    #ax6.tick_params(axis='x', labelrotation = 90) 
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='dia/png')


@app.route('/visitantes.html', methods=['POST'])
def visitantes():
    if request.method == 'POST':
        nombre = request.form['name']
        apellido = request.form['last_name']
        hora_e = time.strftime("%H:%M:%S")
        tipo_usuario = request.form['tipo_usuario']
        if tipo_usuario == 'Estudiante':
            departamento = 'Comunidad Universitaria'
            descripcion = None
        else:
            departamento = request.form['departamento']
            descripcion = request.form['descripcion']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO registro (nombre,apellido,he,motivo_ingreso,departamento,descripcion,fecha) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                    (nombre, apellido, hora_e, tipo_usuario, departamento, descripcion, date))
        mysql.connection.commit()
        return redirect(url_for('visitantes'))

@app.route('/visitantes.html', methods=['GET'])
def visitantes_get():
    return render_template('/visitantes.html')

@app.route('/bitacora.html')
def bitacora():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM registro WHERE fecha = %s',(date,))
    data = cur.fetchall()
    cur.close()
    return render_template('/bitacora.html', registros = data)

@app.route('/filtrar_fecha', methods=['POST'])
def bitacora_filtrar_fecha():
    cur = mysql.connection.cursor()
    fecha_inicio = request.form['fecha-inicio']
    fecha_fin = request.form['fecha-fin']
    if fecha_fin == "":
        fecha_fin = fecha_inicio
    cur.execute('SELECT * FROM registro WHERE fecha BETWEEN %s AND %s',(fecha_inicio,fecha_fin))
    data = cur.fetchall()
    cur.close()
    return render_template('/bitacora.html', registros = data)

@app.route('/exit/<id>')
def registro_salida(id):
    hora_s = time.strftime("%H:%M:%S")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE registro SET hs = %s WHERE id_registro = %s", (hora_s, id))
    mysql.connection.commit()
    return redirect(url_for('bitacora'))

if __name__ == '__main__':
    print()
    app.run(port=3000, debug=True)