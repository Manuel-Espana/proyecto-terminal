import pandas as pd
from matplotlib.figure import Figure
import numpy as np
import base64
import io
import plotly
import plotly.graph_objs as go
import json

def eH():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    #Modificacion de la hora de entrada
    data.he = pd.to_datetime(data.he)
    data.he = data.he.dt.floor('H').dt.time
    fhorae = data.groupby('he').size().reset_index(name = 'frecuencia')
    fhorae = fhorae.sort_values(by = 'frecuencia', ascending = False)
    fhorae = fhorae.head(6)

    #Grafica las horas con mas ingresos
    bar = [go.Bar(x = fhorae.he,  y = fhorae.frecuencia, marker_color='dodgerblue')]
    data = go.Figure(bar)
    data.update_layout(title = 'Horas con más ingresos en el mes de enero', xaxis_title = 'Horas', yaxis_title = 'Cantidad de ingresos')
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def oH():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    #Modificacion de la hora de salida
    data.hs = pd.to_datetime(data.hs)
    data.hs = data.hs.dt.floor('H').dt.time
    fhoras = data.groupby('hs').size().reset_index(name = 'frecuencia')
    fhoras = fhoras.sort_values(by = 'frecuencia', ascending = False)
    fhoras = fhoras.head(6)

    #Grafica las horas con mas salidas
    bar = [go.Bar(x = fhoras.hs,  y = fhoras.frecuencia, marker_color='orangered')]
    data = go.Figure(bar)
    data.update_layout(title = 'Horas con más salidas en el mes de enero', xaxis_title = 'Horas', yaxis_title = 'Cantidad de salidas')
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def users():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    #Modificacion de los usuarios
    fmotivo = data.groupby('motivo_ingreso').size().reset_index(name = 'frecuencia')

    #Grafica los usuarios
    pie = [go.Pie(labels = fmotivo.motivo_ingreso, values = fmotivo.frecuencia)]
    data = go.Figure(pie)
    data.update_layout(title = 'Usuarios en el mes de enero')
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def departament():
    #Lectura del csv
    df = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    fdepa = df.groupby('departamento').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor y solo muestra los primeros 7
    fdepa = fdepa.sort_values(by = 'frecuencia', ascending = False)
    fdepa = fdepa.head(7)

    # #Grafica los departamento
    colors = ['deepskyblue', 'mediumpurple', 'darkorange', 'gold', 'teal', 'violet', 'crimson']
    bar = [go.Bar(x = fdepa.departamento,  y = fdepa.frecuencia, marker_color = colors)]
    data = go.Figure(bar)
    data.update_layout(title = 'Departamentos más visitados en el mes de enero', xaxis_title = 'Departamentos', yaxis_title = 'Cantidad de visitas')
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def dates():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    ffecha = data.groupby('fecha').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor y solo muestra los primeros 7
    ffecha = ffecha.sort_values(by = 'frecuencia', ascending = False)
    ffecha = ffecha.head(7)

    #Grafica los departamento
    colors = ['darkred', 'seagreen', 'mediumslateblue', 'dodgerblue', 'sandybrown', 'mediumvioletred', 'cornflowerblue']
    bar = [go.Bar(x = ffecha.fecha,  y = ffecha.frecuencia, marker_color = colors)]
    data = go.Figure(bar)
    data.update_layout(title = 'Fechas con más flujo en el mes de enero', xaxis_title = 'Fechas', yaxis_title = 'Cantidad de ingresos')
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def dWeek():
    #Lectura del csv
    data = pd.read_csv("static/Base de datos (bitacora) - Copia de Total.csv")
    #Conversion a tipo fecha y a dia de la semana
    data.fecha = pd.to_datetime(data.fecha)
    data.fecha = data.fecha.dt.strftime('%A')
    dia = data.groupby('fecha').size().reset_index(name = 'frecuencia')
    #Orderna de mayor a menor
    dia = dia.sort_values(by = 'frecuencia', ascending = False)

    #Grafica los dias de la semana
    colors = ['darkorange', 'darkorchid', 'darkcyan', 'darksalmon', 'forestgreen', 'darkslateblue', 'brown']
    bar = [go.Bar(x = dia.fecha,  y = dia.frecuencia, marker_color = colors)]
    data = go.Figure(bar)
    data.update_layout(title = 'Días de la semana con más flujo en el mes de enero', xaxis_title = 'Días', yaxis_title = 'Cantidad de ingresos')
    graphJSON = json.dumps(data, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON