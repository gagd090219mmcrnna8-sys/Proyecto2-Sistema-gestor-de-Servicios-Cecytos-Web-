import mysql.connector

def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rout123",
        database="cecytos_servicios"
    )

    return conexion