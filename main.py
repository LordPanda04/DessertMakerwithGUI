from flask import Flask, render_template, request, send_from_directory
import csv
import pandas as pd

app = Flask(__name__)

postre_ingredientes_cantidades ={}
stockIngrediente_cantidad={}

postreExtraido=""
interseccion_ingredientes=set()
diferencia_ingredientes=set()
ingrediente_cantidadFaltante={}

def recopilar_postres():
  global postre_ingredientes_cantidades
  
  with open ("static/csv/postres.csv","r") as archivo:
    csv_reader=csv.reader(archivo)
    encabezado=next(csv_reader)

    for fila in csv_reader:
      postre=fila[0]
      ingrediente=fila[1]
      cantidad=fila[2]

      if postre in postre_ingredientes_cantidades:
        ingredientes,cantidades=postre_ingredientes_cantidades[postre]
        ingredientes.append(ingrediente)
        cantidades.append(cantidad)
        postre_ingredientes_cantidades[postre]=ingredientes,cantidades

      else:
        ingredientes=[]
        ingredientes.append(ingrediente)
        cantidades=[]
        cantidades.append(cantidad)
        postre_ingredientes_cantidades[postre]=ingredientes,cantidades


def buscar_ingrediente(codigo_ingrediente):
  with open ("static/csv/ingredientes.csv","r") as archivo:
    csv_reader=csv.reader(archivo)
    encabezado=next(csv_reader)

    for columna in csv_reader:
      codigo=columna[0]
      ingrediente=columna[1]
      unidad=columna[2]

      if(codigo_ingrediente==codigo):
        return True,ingrediente

    return False,None

def extraer_receta():
  global postre_ingredientes_cantidades
  global stockIngrediente_cantidad  
  global postreExtraido
  global interseccion_ingredientes
  global diferencia_ingredientes
  global ingrediente_cantidadFaltante
  
  stockIngredientes=stockIngrediente_cantidad.keys()
  stockIngredientes=set(stockIngredientes)

  postres=postre_ingredientes_cantidades.keys()

  max_interseccion_ingredientes=0
  interseccion_ingredientes=set()

  for postre in postres:
    ingredientes,cantidades=postre_ingredientes_cantidades[postre]
    ingredientes=set(ingredientes)
    interseccion=ingredientes.intersection(stockIngredientes)
    diferencia=ingredientes.difference(stockIngredientes)

    if(len(interseccion)>max_interseccion_ingredientes):
      max_interseccion_ingredientes=len(interseccion)
      postreExtraido=postre
      interseccion_ingredientes=interseccion
      diferencia_ingredientes=diferencia

  ingredientes,cantidades=postre_ingredientes_cantidades[postreExtraido]
  ingrediente_cantidad={}
  i=0
  for ingrediente in ingredientes:
    ingrediente_cantidad[ingrediente]=cantidades[i]
    i+=1

  for ingrediente in interseccion_ingredientes:
    if float(ingrediente_cantidad[ingrediente])>float(stockIngrediente_cantidad[ingrediente]):
      ingrediente_cantidadFaltante[ingrediente]=float(ingrediente_cantidad[ingrediente])-float(stockIngrediente_cantidad[ingrediente])

    else:
      ingrediente_cantidadFaltante[ingrediente]=0
      


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)
  
@app.route('/')
def home():
    global stockIngrediente_cantidad
    global postreExtraido
    global interseccion_ingredientes
    global diferencia_ingredientes
    global ingrediente_cantidadFaltante
  
    stockIngrediente_cantidad={}
    postreExtraido=""
    interseccion_ingredientes=set()
    diferencia_ingredientes=set()
    ingrediente_cantidadFaltante={}
  
    return render_template('home.html',stockIngrediente_cantidad=stockIngrediente_cantidad)

@app.route('/ingredientes')
def ingredientes():
    stockIngrediente_cantidad={}
  
    df=pd.read_csv('static/csv/ingredientes.csv')
    ingredientes_data = df.to_html(index=False)

    return render_template('ingredientes.html',ingredientes_data=ingredientes_data,stockIngrediente_cantidad=stockIngrediente_cantidad)


@app.route('/anadirIngrediente',methods=['POST'])
def anadirIngrediente():
  df=pd.read_csv('static/csv/ingredientes.csv')
  ingredientes_data = df.to_html(index=False)
  
  codigoIngrediente=request.form.get("codigo")  
  cantidadIngrediente=request.form.get("cantidad")  
  ingredienteExiste,ingrediente=buscar_ingrediente(codigoIngrediente)

  if ingredienteExiste:
    stockIngrediente_cantidad[ingrediente]=cantidadIngrediente

  return render_template('ingredientes.html',ingredientes_data=ingredientes_data,stockIngrediente_cantidad=stockIngrediente_cantidad)


@app.route('/postre')
def postre():
  recopilar_postres()
  extraer_receta()
  return render_template('postre.html',postreExtraido=postreExtraido,interseccion_ingredientes=interseccion_ingredientes, diferencia_ingredientes=diferencia_ingredientes, ingrediente_cantidadFaltante=ingrediente_cantidadFaltante)


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)

