import pandas as pd
from matplotlib.figure import Figure
import numpy as np
import base64
import io


def eH():
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
    ax.set_title('Horas con más ingresos en el mes de enero')
    ax.set_ylabel('Cantidad de ingresos')

    #Guarda la grafica y se envia para mostrarse en HTML
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return img


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
    fig = Figure()
    ax2 = fig.add_subplot(111)
    ax2.bar(fhoras.hs.apply(str), fhoras.frecuencia, color = 'orangered')
    ax2.set_title('Horas con más salidas en el mes de enero')
    ax2.set_ylabel('Cantidad de salidas')

    #Guarda la grafica y se envia para mostrarse en HTML
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return img


def users():
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

    #Guarda la grafica y se envia para mostrarse en HTML
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return img


def departament():
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
    ax4.set_title('Departamentos más visitados en el mes de enero')
    ax4.set_ylabel('Cantidad de visitas')
    ax4.bar(fdepa['departamento'], fdepa['frecuencia'], color = ('deepskyblue', 'darkorange', 'slateblue', 'gold', 'teal', 'hotpink', 'crimson'))

    #Guarda la grafica y se envia para mostrarse en HTML
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return img


def dates():
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
    ax5.set_title('Días con más flujo en el mes de enero')
    ax5.set_ylabel('Cantidad de ingresos')
    ax5.bar(ffecha['fecha'], ffecha['frecuencia'], color = 'royalblue')

    #Guarda la grafica y se envia para mostrarse en HTML 
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return img


def dWeek():
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
    ax6.set_title('Días de la semana con más flujo en el mes de enero')
    ax6.set_ylabel('Cantidad de ingresos')
    ax6.bar(dia['fecha'], dia['frecuencia'], color = 'mediumseagreen')
    
    #Guarda la grafica y se envia para mostrarse en HTML
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return img