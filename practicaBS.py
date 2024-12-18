import sqlite3
from tokenize import Double
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re
from datetime import datetime
import os, ssl


# Evitar error SSL
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# Número de páginas a extraer
PAGINAS = 4

# Función para extraer las recetas de las primeras cuatro páginas
def almacenar_bd():
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS RECETAS")
    conn.execute('''CREATE TABLE RECETAS
       (TITULO TEXT NOT NULL,
        FECHA DATE,
        CATEGORIAS TEXT,
        INGREDIENTES TEXT,
        VALORACION REAL,
        VOTOS INT);''')

    # Iterar sobre las primeras 4 páginas
    for pagina in range(1, PAGINAS + 1):
        if pagina == 1:
            url = "https://www.javirecetas.com/receta/recetas-faciles-cocina-facil/"
        else:
            url = f"https://www.javirecetas.com/receta/recetas-faciles-cocina-facil/page/{pagina}/"
        
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        lista_link_recetas = s.find("div", id="contenido").find_all("div", class_="post")
        
        for link_receta in lista_link_recetas:
            
            titulo=link_receta.find("div", class_="titulo").find("a")
            if titulo:  # Verifica si existe el enlace <a>
                titulo = titulo.string.strip().encode('utf-8').decode('utf-8')
            fechaSinStrip = link_receta.find("div").find("small",class_="bajoTitulo").getText().replace("PUBLICADO EL ","").replace(
                " POR JAVI RECETAS","")
            fecha = datetime.strptime(fechaSinStrip.strip(), '%d-%m-%Y').date()
            f = urllib.request.urlopen(link_receta.a['href'])
            s = BeautifulSoup(f, "lxml")
            datos = s.find("div", id="contenido")

            variasCategorias = datos.find("span", class_="categoriasReceta").find_all("a")
            categorias = set()
            if variasCategorias:
                for a in variasCategorias:
                    categoria = a.getText()
                    categorias.add(categoria)
            else:
                categorias.add("Desconocido")


            ingredientes= set()
            variosIngredientes = datos.find("span", class_="ingredientesReceta").find_all("a")
            if not variosIngredientes:
                ingredientes.add("Desconocido")
            else:  
                for a in variosIngredientes:
                    ingredientes.add(a.getText())
            
            valoracion = datos.find("div", class_="post-ratings").getText()
            patron_valoracion = r"Valoración:\s*([\d,]+)"
            resultado_valoracion = re.search(patron_valoracion, valoracion)
            if resultado_valoracion:
                    valoracion = float(resultado_valoracion.group(1).replace(',', '.'))
            else:
                    valoracion = 0.0


            votos = datos.find("div", class_="post-ratings").getText()
            patron_votos = r"Votos:\s*(\d+)"
            resultado_votos = re.search(patron_votos, votos)
            
            if resultado_votos:
                votos = int(resultado_votos.group(1))
            else:
                votos = 0

            # Convertir los sets a strings antes de la inserción
            categorias_str = ', '.join(categorias)
            ingredientes_str = ', '.join(ingredientes)

            conn.execute("INSERT INTO RECETAS (TITULO, FECHA, CATEGORIAS, INGREDIENTES, VALORACION, VOTOS) VALUES (?,?,?,?,?,?)",
                         (titulo, fecha, categorias_str, ingredientes_str, float(valoracion), int(votos)))
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM RECETAS")
    messagebox.showinfo("Base de Datos", f"Se almacenaron {cursor.fetchone()[0]} recetas en la base de datos.")
    conn.close()

# Función para almacenar las recetas en una base de datos SQLite


# Función para listar recetas ordenadas por votos
def listar_recetas():
    conn = sqlite3.connect('recetas.db')
    cursor = conn.execute("SELECT * FROM RECETAS ORDER BY VOTOS DESC")
    imprimir_lista(cursor)
    conn.close()

# Función para listar las tres recetas mejor valoradas
def listar_mejor_valoradas():
    conn = sqlite3.connect('recetas.db')
    cursor = conn.execute("SELECT * FROM RECETAS ORDER BY VALORACION DESC LIMIT 3")
    imprimir_lista(cursor)
    conn.close()

# Función para buscar recetas por categoría
def buscar_por_categoria():
    def listar(event):
        conn = sqlite3.connect('recetas.db')
        cursor = conn.execute("SELECT * FROM RECETAS WHERE CATEGORIAS LIKE ?", ('%' + entry.get() + '%',))
        imprimir_lista(cursor)
        conn.close()

    conn = sqlite3.connect('recetas.db')
    cursor = conn.execute("SELECT CATEGORIAS FROM RECETAS")
    categorias = set()
    for row in cursor:
        categorias_lista = row[0].split(', ')
        for categoria in categorias_lista:
            categorias.add(categoria.strip())
    conn.close()

    v = Toplevel()
    label = Label(v, text="Seleccione una categoría:")
    label.pack(side=LEFT)
    entry = Spinbox(v, values=list(sorted(categorias)))
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

# Función para buscar recetas por ingredientes
def buscar_por_ingrediente():
    def listar(event):
        conn = sqlite3.connect('recetas.db')
        cursor = conn.execute("SELECT * FROM RECETAS WHERE INGREDIENTES LIKE ?", ('%' + entry.get() + '%',))
        imprimir_lista(cursor)
        conn.close()

    conn = sqlite3.connect('recetas.db')
    cursor = conn.execute("SELECT INGREDIENTES FROM RECETAS")
    # Crear un conjunto para almacenar ingredientes únicos
    ingredientes = set()
    for row in cursor:
        # Dividir la cadena de ingredientes y añadir cada ingrediente al conjunto
        ingredientes_lista = row[0].split(', ')
        for ingrediente in ingredientes_lista:
            ingredientes.add(ingrediente.strip())
    conn.close()

    v = Toplevel()
    label = Label(v, text="Seleccione un ingrediente:")
    label.pack(side=LEFT)
    entry = Spinbox(v, values=list(sorted(ingredientes)))  # Ordenar la lista de ingredientes
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

# Función para buscar recetas por fecha y categoría
def buscar_por_fecha_categoria():
    def listar():
        fecha = datetime.strptime(entry_fecha.get(), '%d/%m/%Y').date()
        categoria = spin_categoria.get()

        conn = sqlite3.connect('recetas.db')
        cursor = conn.execute("SELECT * FROM RECETAS WHERE FECHA >= ? AND CATEGORIAS LIKE ?", (fecha, '%' + categoria + '%'))
        imprimir_lista(cursor)
        conn.close()

    conn = sqlite3.connect('recetas.db')
    cursor = conn.execute("SELECT CATEGORIAS FROM RECETAS")
    categorias = set()
    for row in cursor:
        categorias_lista = row[0].split(', ')
        for categoria in categorias_lista:
            categorias.add(categoria.strip())
    conn.close()

    v = Toplevel()
    label_fecha = Label(v, text="Introduzca una fecha (dd/mm/aaaa):")
    label_fecha.pack(side=LEFT)
    entry_fecha = Entry(v)
    entry_fecha.pack(side=LEFT)

    label_categoria = Label(v, text="Seleccione una categoría:")
    label_categoria.pack(side=LEFT)
    spin_categoria = Spinbox(v, values=list(sorted(categorias)))
    spin_categoria.pack(side=LEFT)

    boton_buscar = Button(v, text="Buscar", command=listar)
    boton_buscar.pack(side=LEFT)

# Función para imprimir los resultados en una ventana con Listbox
def imprimir_lista(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    
    for row in cursor:
        lb.insert(END, f"TÍTULO: {row[0]}")
        lb.insert(END, f"FECHA: {row[1]} | CATEGORÍAS: {row[2]}")
        lb.insert(END, f"INGREDIENTES: {row[3]}")
        lb.insert(END, f"VALORACIÓN: {row[4]} | VOTOS: {row[5]}")
        lb.insert(END, "-"*100)
    
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

# Función principal para crear la ventana de Tkinter
def ventana_principal():
    root = Tk()
    root.geometry("300x200")

    menubar = Menu(root)

    # Menú de Datos
    menu_datos = Menu(menubar, tearoff=0)
    menu_datos.add_command(label="Cargar", command=almacenar_bd)
    menu_datos.add_command(label="Salir", command=root.quit)
    menubar.add_cascade(label="Datos", menu=menu_datos)

    # Menú de Listar
    menu_listar = Menu(menubar, tearoff=0)
    menu_listar.add_command(label="Todas ordenadas por votos", command=listar_recetas)
    menu_listar.add_command(label="Mejor valoradas", command=listar_mejor_valoradas)
    menubar.add_cascade(label="Listar", menu=menu_listar)

    # Menú de Buscar
    menu_buscar = Menu(menubar, tearoff=0)
    menu_buscar.add_command(label="Recetas por categorías", command=buscar_por_categoria)
    menu_buscar.add_command(label="Recetas por ingredientes", command=buscar_por_ingrediente)
    menu_buscar.add_command(label="Recetas por fecha y categoría", command=buscar_por_fecha_categoria)
    menubar.add_cascade(label="Buscar", menu=menu_buscar)

    root.config(menu=menubar)
    root.mainloop()

if __name__ == "__main__":
    ventana_principal()
        