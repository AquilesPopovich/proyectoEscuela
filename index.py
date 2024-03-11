import tkinter as tk
from tkinter import ttk, messagebox
import pymongo
from bson.objectid import ObjectId

# Parámetros de conexión a MongoDB
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_TIMEOUT = 2000
MONGO_URL = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

# Nombre de la base de datos y colección
MONGO_BASEDEDATOS = "escuela"
MONGO_COLECCION = "alumnos"

# Conexión a MongoDB y acceso a la colección
client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=MONGO_TIMEOUT)
coleccion = client[MONGO_BASEDEDATOS][MONGO_COLECCION]
ID_ALUMNO = ""

# Función para mostrar los datos en la tabla
def mostrarDatos(nombre="", sexo="", calificacion=""):
    objetoBuscar={}
    if len(nombre) != 0:
        objetoBuscar["nombre"] = nombre
    if len(sexo) != 0:
        objetoBuscar["sexo"] = sexo
    if len(calificacion) != 0:
        objetoBuscar["calificacion"] = calificacion
    tabla.delete(*tabla.get_children())  # Limpiar tabla antes de mostrar datos
    try:
        for documento in coleccion.find(objetoBuscar):
            tabla.insert('', 'end', text=documento["_id"], values=documento["nombre"])
    except pymongo.errors.ServerSelectionTimeoutError as errorTiempo:
        print("Tiempo exedido ", errorTiempo)
    except pymongo.errors.ConnectionFailure as errorConexion:
        print("Fallo al conectarse a MongoDB ", errorConexion)

# Función para crear un nuevo registro
def crearRegistro():
    if nombre.get() and calificacion.get() and sexo.get():
        try:
            new_alumno = {
                "nombre": nombre.get(),
                "calificacion": calificacion.get(),
                "sexo": sexo.get()
            }
            coleccion.insert_one(new_alumno)
            nombre.delete(0, tk.END)
            calificacion.delete(0, tk.END)
            sexo.delete(0, tk.END)  
            mostrarDatos()  # Actualizar tabla después de agregar el nuevo registro
        except pymongo.errors.ConnectionFailure as errorConexion:
            print("Fallo al conectarse a MongoDB ", errorConexion)
    else:
        messagebox.showerror(message="Los campos no pueden estar vacíos")

# Función para manejar el doble clic en la tabla
def dobleClickTabla(event):
    global ID_ALUMNO
    ID_ALUMNO = str(tabla.item(tabla.selection())['text'])
    alumnoSeleccionado = coleccion.find_one({"_id": ObjectId(ID_ALUMNO)})
    nombre.delete(0, tk.END)
    nombre.insert(tk.END, alumnoSeleccionado["nombre"])
    calificacion.delete(0, tk.END)
    calificacion.insert(tk.END, alumnoSeleccionado["calificacion"])
    sexo.delete(0, tk.END) 
    sexo.insert(tk.END, alumnoSeleccionado["sexo"])
    crear["state"] = "disabled"
    editar["state"] = "normal"
    borrar["state"] = "normal"

# Función para editar un alumno
def editarAlumno():
    global ID_ALUMNO
    if nombre.get() and calificacion.get() and sexo.get():
        try:
            idEditar = {"_id": ObjectId(ID_ALUMNO)}
            newValues = {
                "nombre": nombre.get(),
                "calificacion": calificacion.get(),
                "sexo": sexo.get()
            }
            coleccion.update_one(idEditar, {"$set": newValues})
            nombre.delete(0, tk.END)
            calificacion.delete(0, tk.END)
            sexo.delete(0, tk.END)  
        except pymongo.errors.ConnectionFailure as errorConexion:
            print("Fallo al conectarse a MongoDB ", errorConexion)
    else: 
         messagebox.showerror(message="Los campos no pueden estar vacíos")
    mostrarDatos()
    crear["state"] = "normal"
    editar["state"] = "disabled"
    borrar["state"] = "disabled"

# Función para borrar un alumno
def borrarAlumno():
    global ID_ALUMNO
    try:
        idBuscar = {"_id": ObjectId(ID_ALUMNO)}
        coleccion.delete_one(idBuscar)
        nombre.delete(0, tk.END)
        calificacion.delete(0, tk.END)
        sexo.delete(0, tk.END) 
    except pymongo.errors.ConnectionFailure as errorConexion:
        print("Fallo al conectarse a MongoDB ", errorConexion)
    mostrarDatos()
    crear["state"] = "normal"
    editar["state"] = "disabled"
    borrar["state"] = "disabled"

def buscarAlumno():
    mostrarDatos(buscarNombre.get(), buscarSexo.get(), buscarCalificacionAlumno.get())

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Registro de Alumnos")

# Crear tabla
tabla = ttk.Treeview(ventana, columns=("#0", "#1"))
tabla.grid(row=1, column=0, columnspan=2)
tabla.heading("#0", text="ID")
tabla.heading("#1", text="NOMBRE")
tabla.bind("<Double-Button-1>", dobleClickTabla)
mostrarDatos()  # Mostrar datos al iniciar la ventana

# Crear campos de entrada y etiquetas
tk.Label(ventana, text="Nombre").grid(row=2, column=0)
nombre = tk.Entry(ventana)
nombre.grid(row=2, column=1)

tk.Label(ventana, text="Sexo").grid(row=3, column=0)
sexo = tk.Entry(ventana)
sexo.grid(row=3, column=1)

tk.Label(ventana, text="Calificación").grid(row=4, column=0)
calificacion = tk.Entry(ventana)
calificacion.grid(row=4, column=1)

# Botón para crear un nuevo registro
crear = tk.Button(ventana, text="Crear alumno", command=crearRegistro, bg="green", fg="white")
crear.grid(row=5, columnspan=2)

# Btn editar
editar = tk.Button(ventana, text="Editar alumno", command=editarAlumno, bg="blue", fg="white")
editar.grid(row=6, column=0)
editar["state"] = "disabled"

# Btn borrar
borrar = tk.Button(ventana, text="Borrar alumno", command=borrarAlumno, bg="red", fg="white")
borrar.grid(row=7, column=0)
borrar["state"] = "disabled"

tk.Label(ventana, text="Buscar por nombre").grid(row=8, column=0)
buscarNombre = tk.Entry(ventana)
buscarNombre.grid(row=8, column=1)

tk.Label(ventana, text="Buscar por sexo").grid(row=9, column=0)
buscarSexo = tk.Entry(ventana)
buscarSexo.grid(row=9, column=1)

tk.Label(ventana, text="Buscar por calificación").grid(row=10, column=0)
buscarCalificacionAlumno = tk.Entry(ventana)
buscarCalificacionAlumno.grid(row=10, column=1)

borrar = tk.Button(ventana, text="Buscar alumno", command=buscarAlumno, bg="orange", fg="white")
borrar.grid(row=11, columnspan=2)


# Iniciar bucle principal de la aplicación
ventana.mainloop()
