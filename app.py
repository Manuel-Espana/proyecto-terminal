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

date = datetime.date.today()

#Ajusta automaticamente el tamaño de las graficas
rcParams.update({'figure.autolayout': True})
#Establece configuración para España en sistemas Windows
locale.setlocale(locale.LC_ALL,'esp')

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456789'
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
    img = eH()
    return send_file(img, mimetype='horaE/png')
    
@app.route('/horaS/')
def horaS():
    img = oH()
    return send_file(img, mimetype='horaS/png')

@app.route('/usuarios/')
def usuarios():
    img = users()
    return send_file(img, mimetype='usuarios/png')

@app.route('/depa/')
def depa():
    img = departament()
    return send_file(img, mimetype='depa/png')

@app.route('/fecha/')
def fecha():
    img = dates()
    return send_file(img, mimetype='fecha/png')

@app.route('/dia/')
def dia():
    img = dWeek()
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