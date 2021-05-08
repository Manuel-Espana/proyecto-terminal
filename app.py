from flask import Flask, render_template, url_for, redirect, flash, request, send_file, g, session
from flask_mysqldb import MySQL
from os import urandom
from statistics import mean
from sklearn.metrics import make_scorer, explained_variance_score, mean_absolute_error, mean_squared_log_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from statsmodels.tsa.api import VAR
import datetime
import locale
import time
import pandas as pd
import plotly
import plotly.graph_objs as go
import json
import numpy as np

date = datetime.date.today()

#Establece configuración para España en sistemas Windows
locale.setlocale(locale.LC_ALL,'esp')

app = Flask(__name__)
app.secret_key = urandom(24)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456789'
app.config['MYSQL_DB'] = 'bitacora'
mysql = MySQL(app)

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

#Muestra la sección de esscaneo de código QR
@app.route('/')
def index():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM cuenta WHERE id = %s', (session['user_id'][0],))
        data = cur.fetchall()
        g.user = data

#Muestra la sección de login
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']
        #Consulta del user id para obtener tipo de usuario
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM cuenta WHERE usuario = %s AND password = %s', (username, password))
        data = cur.fetchall()
        if data:
            session['user_id'] = data[0]
            return redirect(url_for('index'))
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

#Inserción a la base de datos por escaneo de código QR
@app.route('/datos_qr', methods = ['POST'])
def datos_qr():
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
        cur.execute('SELECT * FROM usuario WHERE uuid = %s', (uuid,))
        data = cur.fetchall()
        tipo_usuario = data[0][3]
        #Busca si el usuario se encuentra dentro de la institución en la tabla de registros
        cur.execute('SELECT * FROM registro WHERE uuid = %s AND fecha = %s AND hs IS NULL', (uuid, date))
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
        cur.execute('SELECT * FROM usuario WHERE uuid = %s', (uuid,))
        data = cur.fetchall()
        #Busca si el usuario se encuentra dentro de la institución en la tabla de registros
        cur.execute('SELECT * FROM registro WHERE uuid = %s AND fecha = %s AND hs IS NULL', (uuid, date))
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
    cur.execute('SELECT * FROM usuario WHERE uuid = %s', (id,))
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
    if not g.user:
        return redirect(url_for('login'))
    if g.user[0][3] != 2:
        return redirect(url_for('index'))
    he = graf_he()
    hs = graf_hs()
    usuario = graf_usuarios()
    dep = graf_depa()
    fecha = graf_fecha()
    dia = graf_dia()
    personas = pers_activas()
    total = personas_mes()
    return render_template('/resultados.html', plot1 = he, plot2 = hs, plot3 = usuario, plot4 = dep, plot5 = fecha, plot6 = dia, pers = personas, total = total)

#Funcion para mostrar a las personas dentro de la universidad en el dia
def pers_activas():
    #Consulta para obtener las personas del dia de hoy
    cur = mysql.connection.cursor()
    cur.execute('SELECT hs FROM registro WHERE fecha = %s', (date,))
    data = cur.fetchall()
    cur.close()
    df = pd.DataFrame(data, columns = ['hs'])
    #Filtro para obtener a las personas que no han salido
    pers = df.hs.isnull().sum()
    return pers

def personas_mes():
    mes_inicio = '2021-01-01'
    mes_fin ='2021-01-31'
    #Consulta para obtener las personas del mes
    cur = mysql.connection.cursor()
    cur.execute('SELECT he FROM registro WHERE fecha BETWEEN %s AND %s', (mes_inicio, mes_fin))
    data = cur.fetchall()
    cur.close()
    df = pd.DataFrame(data, columns = ['he'])
    #Suma de las personas en el mes
    dataframe = df.groupby('he').size().reset_index(name = 'frecuencia')
    total_mes = dataframe.frecuencia.sum()
    return total_mes

#Despliegue de los dashboards en la sección de resultados
@app.route('/modelos.html')
def modelos():
    if not g.user:
        return redirect(url_for('login'))
    if g.user[0][3] != 2:
        return redirect(url_for('index'))
    dia_sig = graf_modelo_diaSig()
    mantenimiento = graf_modelo_mantenimiento()
    colaborador = graf_modelo_colaborador()
    return render_template('/modelos.html', plot1 = dia_sig, plot2 = mantenimiento, plot3 = colaborador)

#Funciones para la creacion de las graficas de Resultados
def graf_he():
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

def graf_hs():
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

def graf_usuarios():
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

def graf_depa():
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

def graf_fecha():
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

def graf_dia():
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

def graf_modelo_diaSig():
    #Se crea la coneccion con la BD y se hace la consulta
    cur = mysql.connection.cursor()
    cur.execute('SELECT he,hs FROM registro')
    data = cur.fetchall()
    cur.close()
    #La consulta se convierte a un DataFrame para su manipulacion
    df = pd.DataFrame(list(data), columns = ['he','hs'])
    df['he'] = pd.to_datetime(df['he'])
    df['hs'] = pd.to_datetime(df['hs'])
    df['h_diff'] = (df.hs - df.he).dt.total_seconds() / 3600.0
    df['he'] = df['he'].dt.floor('H').dt.time
    df['hs'] = df['hs'].dt.floor('H').dt.time
    dia_sig = df[['h_diff']]
    dia_sig['h_yesterday'] = dia_sig.h_diff.shift()
    dia_sig['h_yesterday_diff'] = dia_sig.h_yesterday.diff()
    dia_sig['h_yesterday-1'] = dia_sig.h_yesterday.shift()
    dia_sig['h_yesterday-1_diff'] = dia_sig['h_yesterday-1'].diff()
    dia_sig = dia_sig.dropna()
    dia_sig = dia_sig.reset_index(drop=True)
    
    X_train, X_test, y_train, y_test = Preparacion(dia_sig)
    rmse_score = make_scorer(rmse, greater_is_better = False)
    model = LinearRegression()
    param_search = {
        'fit_intercept':[True,False], 
        'normalize':[True,False], 
        'copy_X':[True, False]
    }

    tscv = TimeSeriesSplit(n_splits = 10)
    gsearch = GridSearchCV(estimator=model, cv=tscv, param_grid=param_search, scoring = rmse_score)
    gsearch.fit(X_train, y_train)
    best_model = gsearch.best_estimator_

    y_true = y_test.values
    y_pred = best_model.predict(X_test)

    linea1 = go.Scatter(
        x = list(range(len(y_true))),
        y = y_test,
        name = 'Valores reales'
    )

    linea2 = go.Scatter(
        x = list(range(len(y_pred))),
        y = y_pred,
        name = 'Valores predichos'
    )
    data = go.Figure([linea1,linea2])
    data.update_layout(title = '<b>Predicción de tiempo de estadía para el siguiente día</b>', xaxis_title = 'Número de predicción', yaxis_title = 'Tiempo de estadía en horas', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def graf_modelo_mantenimiento():
    #Se crea la coneccion con la BD y se hace la consulta
    cur = mysql.connection.cursor()
    cur.execute('SELECT he,hs,departamento FROM registro')
    data = cur.fetchall()
    cur.close()
    #La consulta se convierte a un DataFrame para su manipulacion
    df = pd.DataFrame(list(data), columns = ['he','hs','departamento'])
    df['he'] = pd.to_datetime(df['he'])
    df['hs'] = pd.to_datetime(df['hs'])
    df['h_diff'] = (df.hs - df.he).dt.total_seconds() / 3600.0
    df['he'] = df['he'].dt.floor('H').dt.time
    df['hs'] = df['hs'].dt.floor('H').dt.time
    rh = df[df['departamento'] == 'Mantenimiento']
    rh = rh[['departamento','h_diff']]
    rh['h_yesterday'] = rh.h_diff.shift()
    rh['h_yesterday_diff'] = rh.h_yesterday.diff()
    rh['h_yesterday-1'] = rh.h_yesterday.shift()
    rh['h_yesterday-1_diff'] = rh['h_yesterday-1'].diff()
    rh = rh.dropna()
    rh = rh.reset_index(drop=True)

    X_train, X_test, y_train, y_test = Preparacion(rh)
    rmse_score = make_scorer(rmse, greater_is_better = False)
    model = LinearRegression()
    param_search = {
        'fit_intercept':[True,False], 
        'normalize':[True,False], 
        'copy_X':[True, False]
    }

    tscv = TimeSeriesSplit(n_splits = 10)
    gsearch = GridSearchCV(estimator=model, cv=tscv, param_grid=param_search, scoring = rmse_score)
    gsearch.fit(X_train, y_train)
    best_model = gsearch.best_estimator_

    y_true = y_test.values
    y_pred = best_model.predict(X_test)

    linea1 = go.Scatter(
        x = list(range(len(y_true))),
        y = y_test,
        name = 'Valores reales'
    )

    linea2 = go.Scatter(
        x = list(range(len(y_pred))),
        y = y_pred,
        name = 'Valores predichos'
    )
    data = go.Figure([linea1,linea2])
    data.update_layout(title = '<b>Predicción de tiempo de estadía para el departamento de Mantenimiento</b>', xaxis_title = 'Número de predicción', yaxis_title = 'Tiempo de estadía en horas', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def graf_modelo_colaborador():
    #Se crea la coneccion con la BD y se hace la consulta
    cur = mysql.connection.cursor()
    cur.execute('SELECT he,hs,motivo_ingreso FROM registro')
    data = cur.fetchall()
    cur.close()
    #La consulta se convierte a un DataFrame para su manipulacion
    df = pd.DataFrame(list(data), columns = ['he','hs','motivo_ingreso'])
    df['he'] = pd.to_datetime(df['he'])
    df['hs'] = pd.to_datetime(df['hs'])
    df['h_diff'] = (df.hs - df.he).dt.total_seconds() / 3600.0
    df['he'] = df['he'].dt.floor('H').dt.time
    df['hs'] = df['hs'].dt.floor('H').dt.time
    colaborador = df[df['motivo_ingreso'] == 'Colaborador']
    colaborador = colaborador[['motivo_ingreso','h_diff']]
    colaborador['h_yesterday'] = colaborador.h_diff.shift()
    colaborador['h_yesterday_diff'] = colaborador.h_yesterday.diff()
    colaborador['h_yesterday-1'] = colaborador.h_yesterday.shift()
    colaborador['h_yesterday-1_diff'] = colaborador['h_yesterday-1'].diff()
    colaborador = colaborador.dropna()
    colaborador = colaborador.reset_index(drop=True)

    X_train, X_test, y_train, y_test = Preparacion(colaborador)
    rmse_score = make_scorer(rmse, greater_is_better = False)
    model = LinearRegression()
    param_search = {
        'fit_intercept':[True,False], 
        'normalize':[True,False], 
        'copy_X':[True, False]
    }

    tscv = TimeSeriesSplit(n_splits = 10)
    gsearch = GridSearchCV(estimator=model, cv=tscv, param_grid=param_search, scoring = rmse_score)
    gsearch.fit(X_train, y_train)
    best_model = gsearch.best_estimator_

    y_true = y_test.values
    y_pred = best_model.predict(X_test)

    linea1 = go.Scatter(
        x = list(range(len(y_true))),
        y = y_test,
        name = 'Valores reales'
    )

    linea2 = go.Scatter(
        x = list(range(len(y_pred))),
        y = y_pred,
        name = 'Valores predichos'
    )
    data = go.Figure([linea1,linea2])
    data.update_layout(title = '<b>Predicción de tiempo de estadía para Colaboradores</b>', xaxis_title = 'Número de predicción', yaxis_title = 'Tiempo de estadía en horas', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def Resultados_Regresion(y_true, y_pred):
    #Métricas de regresión
    mae = mean_absolute_error(y_true, y_pred) 
    mse = mean_squared_error(y_true, y_pred) 
    r2 = r2_score(y_true, y_pred)
    print('R2: ', round(r2,4))
    print('MAE: ', round(mae,4))
    print('RMSE: ', round(np.sqrt(mse),4))
    print('Promedio valor real', round(mean(y_true), 3))
    print('Promedio valor predicho', round(mean(y_pred), 3))

def rmse(actual, predict):
    predict = np.array(predict)
    actual = np.array(actual)
    distance = predict - actual
    square_distance = distance ** 2
    mean_square_distance = square_distance.mean()
    score = np.sqrt(mean_square_distance)
    return score

def Preparacion(df):
    X = df[['h_yesterday','h_yesterday_diff', 'h_yesterday-1','h_yesterday-1_diff']]
    y = df.h_diff
    train_size = int(len(df) * 0.80)
    X_train, X_test = X[0:train_size], X[train_size:len(X)]
    y_train, y_test = y[0:train_size], y[train_size:len(X)]
    return X_train, X_test, y_train, y_test

#Registro de visitantes en la sección de visitantes
@app.route('/visitantes.html', methods=['POST'])
def visitantes():
    if(request.method == 'POST'):
        #Obtiene los datos del usuario desde el método POST
        nombre = request.form['nombre']
        apellido = request.form['apellidos']
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
    if not g.user:
        return redirect(url_for('login'))
    return render_template('/visitantes.html')

#Muestra la sección de bitácora, por defecto despliega los registros del día actual
@app.route('/bitacora.html')
def bitacora():
    if not g.user:
        return redirect(url_for('login'))
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
    app.run(port = 3000, debug = True)