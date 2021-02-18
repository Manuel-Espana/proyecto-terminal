from flask import Flask, render_template, url_for, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost:3000'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_db'] = ''

mysql = MySQL()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultados.html')
def resultados():
    return render_template('resultados.html')

@app.route('/visitantes.html')
def visitantes():
    return render_template('visitantes.html')

@app.route('/bitacora.html')
def bitacora():
    return render_template('bitacora.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)
