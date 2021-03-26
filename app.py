from flask import Flask, render_template, url_for, redirect, flash, request, send_file
from flask_mysqldb import MySQL
import datetime
import locale
import time
from dashboard import eH
from dashboard import oH
from dashboard import users
from dashboard import departament
from dashboard import dates
from dashboard import dWeek
from matplotlib import rcParams
import json

date = datetime.date.today()

#Ajusta automaticamente el tamaño de las graficas
rcParams.update({'figure.autolayout': True})
#Establece configuración para España en sistemas Windows
locale.setlocale(locale.LC_ALL,'esp')

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
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
        hora_e = time.strftime("%H:%M:%S")
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
    hora_e = time.strftime("%H:%M:%S")
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

#Registro de visitantes en la sección de visitantes
@app.route('/visitantes.html', methods=['POST'])
def visitantes():
    if(request.method == 'POST'):
        #Obtiene los datos del usuario desde el método POST
        nombre = request.form['name']
        apellido = request.form['last_name']
        hora_e = time.strftime("%H:%M:%S")
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
    cur.execute('SELECT * FROM registro WHERE fecha = %s',(date,))
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
    cur.execute('SELECT * FROM registro WHERE fecha BETWEEN %s AND %s',(fecha_inicio,fecha_fin))
    data = cur.fetchall()
    cur.close()
    return render_template('/bitacora.html', registros = data)

#Actualiza usuario mediante el id de registro, registra hora de salida
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