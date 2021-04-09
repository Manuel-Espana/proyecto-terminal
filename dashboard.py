from flask import Flask, render_template, url_for, redirect, flash, request, send_file
from flask_mysqldb import MySQL
import pandas as pd
import plotly
import plotly.graph_objs as go
import json
import datetime

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bitacora'
mysql = MySQL(app)

def eH():
    #Consulta de los registros de la base de datos
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
    #Consulta de los registros de la base de datos
    cur = mysql.connection.cursor()
    cur.execute('SELECT motivo_ingreso FROM registro')
    data = cur.fetchall()
    cur.close()
    df = pd.DataFrame(data, columns = ['motivo_ingreso'])
    #Modificacion de los usuarios
    fmotivo = df.groupby('motivo_ingreso').size().reset_index(name = 'frecuencia')



def departament():
    #Consulta de los registros de la base de datos
    cur = mysql.connection.cursor()
    cur.execute('SELECT departamento FROM registro')
    data = cur.fetchall()
    cur.close()
    df = pd.DataFrame(data, columns = ['departamento'])
    fdepa = df.groupby('departamento').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor y solo muestra los primeros 7
    fdepa = fdepa.sort_values(by = 'frecuencia', ascending = False)
    fdepa = fdepa.head(7)



def dates():
    #Consulta de los registros de la base de datos
    cur = mysql.connection.cursor()
    cur.execute('SELECT fecha FROM registro')
    data = cur.fetchall()
    cur.close()
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
    data.update_layout(title = '<b>Fechas con más ingresos en el mes de enero 2021</b>', xaxis_title = 'Fechas', yaxis_title = 'Cantidad de ingresos', title_font_size = 15)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def dWeek():
    #Consulta de los registros de la base de datos
    cur = mysql.connection.cursor()
    cur.execute('SELECT fecha FROM registro')
    data = cur.fetchall()
    cur.close()
    df = pd.DataFrame(data, columns = ['fecha'])
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
    data.update_layout(title = '<b>Días de la semana con más ingresos en el mes de enero 2021</b>', xaxis_title = 'Días', yaxis_title = 'Cantidad de ingresos', title_font_size = 12)
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON