from flask import Flask, render_template, url_for, redirect, flash, request
from flask_mysqldb import MySQL
import datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'anselmo10'
app.config['MYSQL_DB'] = 'bitacora'
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/resultados.html')
def resultados():
    return render_template('resultados.html')


@app.route('/visitantes.html', methods=['POST'])
def visitantes():
    date = datetime.date.today()
    if request.method == 'POST':
        nombre = request.form['name']
        apellido = request.form['last_name']
        hora_e = request.form['he']
        hora_s = request.form['hs']
        tipo_usuario = request.form['tipo_usuario']
        departamento = request.form['departamento']
        descripcion = request.form['descripcion']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO registro (nombre,apellido,he,hs,motivo_ingreso,departamento,descripcion,fecha)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                    (nombre, apellido, hora_e, hora_s, tipo_usuario, departamento, descripcion, date))
        mysql.connection.commit()
        return redirect(url_for('visitantes'))


@app.route('/visitantes.html', methods=['GET'])
def visitantes_get():
    return render_template('/visitantes.html')


@app.route('/bitacora.html')
def bitacora():
    return render_template('bitacora.html')


if __name__ == '__main__':
    app.run(port=3000, debug=True)
