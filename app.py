from flask import Flask, render_template, url_for, redirect, flash, request, send_file
from flask_mysqldb import MySQL
import datetime
import locale
import time
import pandas as pd
import plotly
import plotly.graph_objs as go
import json

date = datetime.date.today()

#Establece configuración para España en sistemas Windows
locale.setlocale(locale.LC_ALL,'esp')

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456789'
app.config['MYSQL_DB'] = 'bitacora'
mysql = MySQL(app)

#Muestra la sección de esscaneo de código QR
@app.route('/')
def index():
    return render_template('index.html')
    
#Inserción a la base de datos por escaneo de código QR
@app.route('/datosQR', methods = ['POST'])
def postmethod():
    if(request.method == 'POST'):
        #Obtiene JSON del código QR y se extraen los datos
        usuario = json.loads(request.get_json())
        nombre = usuario["nombre"]
        apellido = usuario["apellido"]
        uuid = usuario['uuid']
        hora_e = time.strftime("%Y-%m-%d %H:%M:%S")
        departamento = 'Comunidad Universitaria'
        descripcion = None
        #Consulta del user id para obtener tipo de usuario
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE uuid = %s',(uuid,))
        data = cur.fetchall()
        tipo_usuario = data[0][3]
        #Busca si el usuario se encuentra dentro de la institución en la tabla de registros
        cur.execute('SELECT * FROM registro WHERE uuid = %s AND fecha = %s AND hs IS NULL',(uuid,date))
        flag = cur.fetchall()
        #Si no está dentro de la institución, inserta registro
        if(not flag):
            cur.execute('INSERT INTO registro (nombre,apellido,he,motivo_ingreso,departamento,descripcion,fecha,uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', 
                        (nombre, apellido, hora_e, tipo_usuario, departamento, descripcion, date, uuid))
        mysql.connection.commit()
        return 'OK', 200

#Función de búsqueda de usuario en la sección de escaneo de QR
@app.route('/buscar_usuario', methods=['POST'])
def busqueda():
    if(request.method == 'POST'):
        cur = mysql.connection.cursor()
        uuid = request.form['uuid']
        #Consulta del user id para obtener datos del usuario
        cur.execute('SELECT * FROM usuario WHERE uuid = %s',(uuid,))
        data = cur.fetchall()
        #Busca si el usuario se encuentra dentro de la institución en la tabla de registros
        cur.execute('SELECT * FROM registro WHERE uuid = %s AND fecha = %s AND hs IS NULL',(uuid,date))
        consult = cur.fetchall()
        flag = False
        if(consult):
            flag = True
        cur.close()
    return render_template('index.html', usuarios = data, flag = flag)

#Registro de usuario desde tabla de resultados de la búsqueda de usuario
@app.route('/register/<id>')
def busqueda_registro(id):
    hora_e = time.strftime("%Y-%m-%d %H:%M:%S")
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuario WHERE uuid = %s',(id,))
    data = cur.fetchall()
    nombre = data[0][1]
    apellido = data[0][2]
    tipo_usuario = data[0][3]
    departamento = 'Comunidad Universitaria'
    descripcion = None
    cur.execute('INSERT INTO registro (nombre,apellido,he,motivo_ingreso,departamento,descripcion,fecha,uuid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', 
                        (nombre, apellido, hora_e, tipo_usuario, departamento, descripcion, date, id))
    mysql.connection.commit()
    return redirect(url_for('index'))

#Despliegue de los dashboards en la sección de resultados
@app.route('/resultados.html')
def resultados():
    eh = eH()
    oh = oH()
    usuario = users()
    dep = departament()
    fecha = dates()
    dia = dWeek()
    return render_template('/resultados.html', plot1 = eh, plot2 = oh, plot3 = usuario, plot4 = dep, plot5 = fecha, plot6 = dia)

#Funciones para la creacion de las graficas de Resultados
def eH():
    #Se crea la coneccion con la BD y se hace la consulta
    cur = mysql.connection.cursor()
    cur.execute('SELECT he FROM registro')
    data = cur.fetchall()
    cur.close()
    df = pd.DataFrame(data, columns = ['he'])
    df['he'] = df['he'].dt.strftime('%H:%M:%S')
    #Modificacion de la hora de entrada
    df.he = pd.to_datetime(df.he)
    df.he = df.he.dt.floor('H').dt.time
    fhorae = df.groupby('he').size().reset_index(name = 'frecuencia')
    fhorae = fhorae.sort_values(by = 'frecuencia', ascending = False)
    fhorae = fhorae.head(6)

    #Grafica las horas con mas ingresos, se guarda como JSON y se envia para graficar
    bar = [go.Bar(x = fhorae.he,  y = fhorae.frecuencia, marker_color='dodgerblue')]
    data = go.Figure(bar)
    data.update_layout(title = '<b>Horas con más ingresos (enero 2021)</b>', xaxis_title = 'Horas', yaxis_title = 'Cantidad de ingresos', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def oH():
    #Consulta de los registros de la base de datos
    cur = mysql.connection.cursor()
    cur.execute('SELECT hs FROM registro')
    data = cur.fetchall()
    cur.close()
    df = pd.DataFrame(data, columns = ['hs'])
    df['hs'] = df['hs'].dt.strftime('%H:%M:%S')
    #Modificacion de la hora de salida
    df.hs = pd.to_datetime(df.hs)
    df.hs = df.hs.dt.floor('H').dt.time
    fhoras = df.groupby('hs').size().reset_index(name = 'frecuencia')
    fhoras = fhoras.sort_values(by = 'frecuencia', ascending = False)
    fhoras = fhoras.head(6)

    #Grafica las horas con mas salidas, se guarda como JSON y se envia para graficar
    bar = [go.Bar(x = fhoras.hs,  y = fhoras.frecuencia, marker_color='orangered')]
    data = go.Figure(bar)
    data.update_layout(title = '<b>Horas con más salidas (enero 2021)</b>', xaxis_title = 'Horas', yaxis_title = 'Cantidad de salidas', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def users():
    #Se crea la coneccion con la BD y se hace la consulta
    cur = mysql.connection.cursor()
    cur.execute('SELECT motivo_ingreso FROM registro')
    data = cur.fetchall()
    cur.close()
    #La consulta se convierte a un DataFrame para su manipulacion
    df = pd.DataFrame(list(data), columns = ['motivo_ingreso'])

    #Modificacion de los usuarios
    fmotivo = df.groupby('motivo_ingreso').size().reset_index(name = 'frecuencia')

    #Grafica los usuarios, se guarda como JSON y se envia para graficar
    pie = [go.Pie(labels = fmotivo.motivo_ingreso, values = fmotivo.frecuencia)]
    data = go.Figure(pie)
    data.update_layout(title = '<b>Usuarios en el mes de enero 2021</b>', title_font = dict(size = 15))
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def departament():
    #Se crea la coneccion con la BD y se hace la consulta
    cur = mysql.connection.cursor()
    cur.execute('SELECT departamento FROM registro')
    data = cur.fetchall()
    cur.close()
    #La consulta se convierte a un DataFrame para su manipulacion
    df = pd.DataFrame(list(data), columns = ['departamento'])

    fdepa = df.groupby('departamento').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor y solo muestra los primeros 7
    fdepa = fdepa.sort_values(by = 'frecuencia', ascending = False)
    fdepa = fdepa.head(7)

    # #Grafica los departamento, se guarda como JSON y se envia para graficar
    colors = ['deepskyblue', 'mediumpurple', 'darkorange', 'gold', 'teal', 'violet', 'crimson']
    bar = [go.Bar(x = fdepa.departamento,  y = fdepa.frecuencia, marker_color = colors)]
    data = go.Figure(bar)
    data.update_layout(title = '<b>Departamentos más visitados (enero 2021)</b>', xaxis_title = 'Departamentos', yaxis_title = 'Cantidad de visitas', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def dates():
    #Se crea la coneccion con la BD y se hace la consulta
    cur = mysql.connection.cursor()
    cur.execute('SELECT fecha FROM registro')
    data = cur.fetchall()
    cur.close()
    #La consulta se convierte a un DataFrame para su manipulacion
    df = pd.DataFrame(data, columns = ['fecha'])
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['fecha'] = df['fecha'].dt.strftime('%Y/%m/%d')
    
    ffecha = df.groupby('fecha').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor y solo muestra los primeros 7
    ffecha = ffecha.sort_values(by = 'frecuencia', ascending = False)
    ffecha = ffecha.head(7)
    
    #Grafica los departamento, se guarda como JSON y se envia para graficar
    colors = ['darkred', 'seagreen', 'mediumslateblue', 'dodgerblue', 'sandybrown', 'mediumvioletred', 'cornflowerblue']
    bar = [go.Bar(x = ffecha.fecha,  y = ffecha.frecuencia, marker_color = colors)]
    data = go.Figure(bar)
    data.update_layout(title = '<b>Fechas con más ingresos (enero 2021)</b>', xaxis_title = 'Fechas', yaxis_title = 'Cantidad de ingresos', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def dWeek():
    #Se crea la coneccion con la BD y se hace la consulta
    cur = mysql.connection.cursor()
    cur.execute('SELECT fecha FROM registro')
    data = cur.fetchall()
    cur.close()
    #La consulta se convierte a un DataFrame para su manipulacion
    df = pd.DataFrame(list(data), columns = ['fecha'])

    #Conversion a tipo fecha y a dia de la semana
    df.fecha = pd.to_datetime(df.fecha)
    df.fecha = df.fecha.dt.strftime('%A')
    dia = df.groupby('fecha').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor
    dia = dia.sort_values(by = 'frecuencia', ascending = False)

    #Grafica los dias de la semana, se guarda como JSON y se envia para graficar
    colors = ['darkorange', 'darkorchid', 'darkcyan', 'darksalmon', 'forestgreen', 'darkslateblue', 'brown']
    bar = [go.Bar(x = dia.fecha,  y = dia.frecuencia, marker_color = colors)]
    data = go.Figure(bar)
    data.update_layout(title = '<b>Días de la semana con más ingresos (enero 2021)</b>', xaxis_title = 'Días', yaxis_title = 'Cantidad de ingresos', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

#Registro de visitantes en la sección de visitantes
@app.route('/visitantes.html', methods=['POST'])
def visitantes():
    if(request.method == 'POST'):
        #Obtiene los datos del usuario desde el método POST
        nombre = request.form['name']
        apellido = request.form['last_name']
        hora_e = time.strftime("%Y-%m-%d %H:%M:%S")
        tipo_usuario = request.form['tipo_usuario']
        if(tipo_usuario != 'Visitante'):
            departamento = 'Comunidad Universitaria'
            descripcion = None
        else:
            departamento = request.form['departamento']
            descripcion = request.form['descripcion']
        cur = mysql.connection.cursor()
        #Inserción del registro a la base de datos
        cur.execute('INSERT INTO registro (nombre,apellido,he,motivo_ingreso,departamento,descripcion,fecha) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                    (nombre, apellido, hora_e, tipo_usuario, departamento, descripcion, date))
        mysql.connection.commit()
        return redirect(url_for('visitantes'))

#Muestra la sección de visitantes
@app.route('/visitantes.html', methods=['GET'])
def visitantes_get():
    return render_template('/visitantes.html')

#Muestra la sección de bitácora, por defecto despliega los registros del día actual
@app.route('/bitacora.html')
def bitacora():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_registro,nombre,apellido,DATE_FORMAT(he,'%%H:%%i:%%s'),DATE_FORMAT(hs,'%%H:%%i:%%s'),motivo_ingreso,departamento,descripcion,fecha,uuid FROM registro WHERE fecha = %s", (date,))
    data = cur.fetchall()
    cur.close()
    return render_template('/bitacora.html', registros = data)

#Filtrado de fechas en la sección de bitácora
@app.route('/filtrar_fecha', methods=['POST'])
def bitacora_filtrar_fecha():
    cur = mysql.connection.cursor()
    fecha_inicio = request.form['fecha-inicio']
    fecha_fin = request.form['fecha-fin']
    if(fecha_fin == ""):
        fecha_fin = fecha_inicio
    cur.execute("SELECT id_registro,nombre,apellido,DATE_FORMAT(he,'%%H:%%i:%%s'),DATE_FORMAT(hs,'%%H:%%i:%%s'),motivo_ingreso,departamento,descripcion,fecha,uuid FROM registro WHERE fecha BETWEEN %s AND %s",(fecha_inicio,fecha_fin))
    data = cur.fetchall()
    cur.close()
    return render_template('/bitacora.html', registros = data)

#Actualiza usuario mediante el id de registro, registra hora de salida
@app.route('/exit/<id>')
def registro_salida(id):
    hora_s = time.strftime("%Y-%m-%d %H:%M:%S")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE registro SET hs = %s WHERE id_registro = %s", (hora_s, id))
    mysql.connection.commit()
    return redirect(url_for('bitacora'))

if __name__ == '__main__':
    print()
    app.run(port=3000, debug=True)