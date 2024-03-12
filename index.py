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
def mostrarDatos(nombre="", sexo="", calificacion="", ordenamiento=""):
    objetoBuscar = {}
    if len(nombre) != 0:
        objetoBuscar["nombre"] = nombre
    if len(sexo) != 0:
        objetoBuscar["sexo"] = sexo
    if len(calificacion) != 0:
        objetoBuscar["calificacion"] = calificacion

    tabla.delete(*tabla.get_children())  # Limpiar tabla antes de mostrar datos
    try:
        if ordenamiento == "A-Z":
            cursor = coleccion.find(objetoBuscar).sort("nombre", )
        elif ordenamiento == "Z-A":
            cursor = coleccion.find(objetoBuscar).sort("nombre", )
        elif ordenamiento == "Calif ↑":
            cursor = coleccion.find(objetoBuscar).sort("calificacion", )
        elif ordenamiento == "Calif ↓":
            cursor = coleccion.find(objetoBuscar).sort("calificacion", )
        else:
            cursor = coleccion.find(objetoBuscar)

        for documento in cursor:
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
    editar.grid(row=6, column=0)
    borrar.grid(row=7, column=0)
    crear.grid_forget()

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
    crear.grid(row=5, columnspan=2)
    editar.grid_forget()
    borrar.grid_forget()

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
    crear.grid(row=5, columnspan=2)
    editar.grid_forget()
    borrar.grid_forget()

def buscarAlumno():
    mostrarDatos(buscarNombre.get(), buscarSexo.get(), buscarCalificacionAlumno.get())

def filtrarNombresAscendente():
    mostrarDatos(ordenamiento="A-Z")

def filtrarNombresDescendente():
    mostrarDatos(ordenamiento="Z-A")

def filtrarCalificacionAscendente():
    mostrarDatos(ordenamiento="Calif ↑")

def filtrarCalificacionDescendente():
    mostrarDatos(ordenamiento="Calif ↓")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Registro de Alumnos")

# Crear tabla
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#D3D3D3", foreground="black", rowheight=25, fieldbackground="#D3D3D3")
style.map("Treeview", background=[('selected', 'blue')])

tabla = ttk.Treeview(ventana, columns=("#0", "#1"), style="Custom.Treeview")
tabla.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
tabla.heading("#0", text="ID")
tabla.heading("#1", text="NOMBRE")
tabla.column("#0", width=100)
tabla.column("#1", width=200)
tabla.bind("<Double-Button-1>", dobleClickTabla)
mostrarDatos()  # Mostrar datos al iniciar la ventana

# Crear campos de entrada y etiquetas
tk.Label(ventana, text="Nombre:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
nombre = tk.Entry(ventana)
nombre.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

tk.Label(ventana, text="Sexo:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
sexo = tk.Entry(ventana)
sexo.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

tk.Label(ventana, text="Calificación:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
calificacion = tk.Entry(ventana)
calificacion.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

# Botón para crear un nuevo registro
crear = tk.Button(ventana, text="Crear alumno", command=crearRegistro, bg="green", fg="white")
crear.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Btn editar
editar = tk.Button(ventana, text="Editar alumno", command=editarAlumno, bg="blue", fg="white")
editar.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
editar.grid_remove()  # Ocultar el botón al principio

# Btn borrar
borrar = tk.Button(ventana, text="Borrar alumno", command=borrarAlumno, bg="red", fg="white")
borrar.grid(row=7, column=0, padx=10, pady=5, sticky="ew")
borrar.grid_remove()  # Ocultar el botón al principio

tk.Label(ventana, text="Buscar por nombre:").grid(row=8, column=0, padx=10, pady=5, sticky="e")
buscarNombre = tk.Entry(ventana)
buscarNombre.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

tk.Label(ventana, text="Buscar por sexo:").grid(row=9, column=0, padx=10, pady=5, sticky="e")
buscarSexo = tk.Entry(ventana)
buscarSexo.grid(row=9, column=1, padx=10, pady=5, sticky="ew")

tk.Label(ventana, text="Buscar por calificación:").grid(row=10, column=0, padx=10, pady=5, sticky="e")
buscarCalificacionAlumno = tk.Entry(ventana)
buscarCalificacionAlumno.grid(row=10, column=1, padx=10, pady=5, sticky="ew")

buscar = tk.Button(ventana, text="Buscar alumno", command=buscarAlumno, bg="orange", fg="white")
buscar.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Botones para filtrar por orden de nombres y calificación
filtrarNombresAsc = tk.Button(ventana, text="A-Z", command=filtrarNombresAscendente)
filtrarNombresAsc.grid(row=8, column=2, padx=5, pady=5, sticky="ew")

filtrarNombresDesc = tk.Button(ventana, text="Z-A", command=filtrarNombresDescendente)
filtrarNombresDesc.grid(row=8, column=3, padx=5, pady=5, sticky="ew")

filtrarCalifAsc = tk.Button(ventana, text="Calif ↑", command=filtrarCalificacionAscendente)
filtrarCalifAsc.grid(row=9, column=2, padx=5, pady=5, sticky="ew")

filtrarCalifDesc = tk.Button(ventana, text="Calif ↓", command=filtrarCalificacionDescendente)
filtrarCalifDesc.grid(row=9, column=3, padx=5, pady=5, sticky="ew")

# Configurar expansión de filas y columnas
ventana.rowconfigure(1, weight=1)
ventana.columnconfigure((0, 1), weight=1)

# Iniciar bucle principal de la aplicación
ventana.mainloop()
