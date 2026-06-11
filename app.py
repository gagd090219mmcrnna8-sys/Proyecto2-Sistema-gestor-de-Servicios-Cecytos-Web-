from flask import Flask, render_template, request, redirect, session
from conexion import conectar
from datetime import date
from datetime import datetime

app = Flask(__name__)

app.secret_key = "cecytos_2026"

@app.route('/')
def bienvenida():
    return render_template('bienvenida.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/validar_login', methods=['POST'])
def validar_login():

    correo = request.form['correo']
    password = request.form['password']

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT * FROM usuarios
    WHERE correo=%s
    AND password=%s
    """

    cursor.execute(sql, (correo, password))

    usuario = cursor.fetchone()

    if usuario:

        session['id_usuario'] = usuario['id_usuario']
        session['nombre'] = usuario['nombre']
        session['rol'] = usuario['rol']

        if usuario['rol'] == 'admin':
            return redirect('/admin')

        return redirect('/usuario')

    return "Correo o contraseña incorrectos"


@app.route('/admin')
def admin():

    if 'rol' not in session:
        return redirect('/login')

    if session['rol'] != 'admin':
        return redirect('/login')

    conexion = conectar()
    cursor = conexion.cursor()

    # Usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]

    # Servicios
    cursor.execute("SELECT COUNT(*) FROM servicios")
    total_servicios = cursor.fetchone()[0]

    # Personal
    cursor.execute("SELECT COUNT(*) FROM personal")
    total_personal = cursor.fetchone()[0]

    # Reportes pendientes
    cursor.execute("""
    SELECT COUNT(*)
    FROM reportes
    WHERE estado='Pendiente'
    """)
    pendientes = cursor.fetchone()[0]

    # Reportes en proceso
    cursor.execute("""
    SELECT COUNT(*)
    FROM reportes
    WHERE estado='En Proceso'
    """)
    en_proceso = cursor.fetchone()[0]

    # Reportes finalizados
    cursor.execute("""
    SELECT COUNT(*)
    FROM reportes
    WHERE estado='Finalizado'
    """)
    finalizados = cursor.fetchone()[0]

    return render_template(
        'admin.html',
        total_usuarios=total_usuarios,
        total_servicios=total_servicios,
        total_personal=total_personal,
        pendientes=pendientes,
        en_proceso=en_proceso,
        finalizados=finalizados
    )

@app.route('/usuario')
def usuario():

    if 'rol' not in session:
        return redirect('/login')

    conexion = conectar()
    cursor = conexion.cursor()

    id_usuario = session['id_usuario']

    cursor.execute("""
    SELECT COUNT(*)
    FROM reportes
    WHERE id_usuario=%s
    """, (id_usuario,))
    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM reportes
    WHERE id_usuario=%s
    AND estado='Pendiente'
    """, (id_usuario,))
    pendientes = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM reportes
    WHERE id_usuario=%s
    AND estado='En Proceso'
    """, (id_usuario,))
    proceso = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM reportes
    WHERE id_usuario=%s
    AND estado='Finalizado'
    """, (id_usuario,))
    finalizados = cursor.fetchone()[0]

    return render_template(
        'usuario.html',
        total=total,
        pendientes=pendientes,
        proceso=proceso,
        finalizados=finalizados
    )


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

@app.route('/usuarios')
def usuarios():

    if 'rol' not in session:
        return redirect('/login')

    if session['rol'] != 'admin':
        return redirect('/login')

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")

    lista_usuarios = cursor.fetchall()

    return render_template(
        'usuarios.html',
        usuarios=lista_usuarios
    )

@app.route('/nuevo_usuario')
def nuevo_usuario():

    return render_template(
        'nuevo_usuario.html'
    )

@app.route('/guardar_usuario', methods=['POST'])
def guardar_usuario():

    nombre = request.form['nombre']
    correo = request.form['correo']
    password = request.form['password']
    rol = request.form['rol']

    fecha = date.today()

    conexion = conectar()

    cursor = conexion.cursor()

    sql = """
    INSERT INTO usuarios
    (
        nombre,
        correo,
        password,
        rol,
        fecha_registro
    )
    VALUES
    (%s,%s,%s,%s,%s)
    """

    cursor.execute(
        sql,
        (
            nombre,
            correo,
            password,
            rol,
            fecha
        )
    )

    conexion.commit()

    return redirect('/usuarios')


@app.route('/eliminar_usuario/<int:id>')
def eliminar_usuario(id):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM usuarios WHERE id_usuario=%s",
        (id,)
    )

    conexion.commit()

    return redirect('/usuarios')


@app.route('/editar_usuario/<int:id>')
def editar_usuario(id):

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM usuarios WHERE id_usuario=%s",
        (id,)
    )

    usuario = cursor.fetchone()

    return render_template(
        'editar_usuario.html',
        usuario=usuario
    )

@app.route('/actualizar_usuario', methods=['POST'])
def actualizar_usuario():

    id_usuario = request.form['id_usuario']
    nombre = request.form['nombre']
    correo = request.form['correo']
    rol = request.form['rol']

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET nombre=%s,
            correo=%s,
            rol=%s
        WHERE id_usuario=%s
    """,
    (
        nombre,
        correo,
        rol,
        id_usuario
    ))

    conexion.commit()

    return redirect('/usuarios')



@app.route('/servicios')
def servicios():

    if 'rol' not in session:
        return redirect('/login')

    if session['rol'] != 'admin':
        return redirect('/login')

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM servicios")

    servicios = cursor.fetchall()

    return render_template(
        'servicios.html',
        servicios=servicios
    )

@app.route('/nuevo_servicio')
def nuevo_servicio():

    return render_template(
        'nuevo_servicio.html'
    )

@app.route('/guardar_servicio', methods=['POST'])
def guardar_servicio():

    nombre = request.form['nombre_servicio']
    descripcion = request.form['descripcion']
    horario = request.form['horario']
    responsable = request.form['responsable']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO servicios
        (
            nombre_servicio,
            descripcion,
            horario,
            responsable
        )
        VALUES
        (%s,%s,%s,%s)
    """,
    (
        nombre,
        descripcion,
        horario,
        responsable
    ))

    conexion.commit()

    return redirect('/servicios')

@app.route('/eliminar_servicio/<int:id>')
def eliminar_servicio(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM servicios WHERE id_servicio=%s",
        (id,)
    )

    conexion.commit()

    return redirect('/servicios')


@app.route('/editar_servicio/<int:id>')
def editar_servicio(id):

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM servicios WHERE id_servicio=%s",
        (id,)
    )

    servicio = cursor.fetchone()

    return render_template(
        'editar_servicio.html',
        servicio=servicio
    )

@app.route('/actualizar_servicio', methods=['POST'])
def actualizar_servicio():

    id_servicio = request.form['id_servicio']

    nombre = request.form['nombre_servicio']

    descripcion = request.form['descripcion']

    horario = request.form['horario']

    responsable = request.form['responsable']

    estado = request.form['estado_servicio']

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    UPDATE servicios
    SET nombre_servicio=%s,
        descripcion=%s,
        horario=%s,
        responsable=%s,
        estado_servicio=%s
    WHERE id_servicio=%s
    """,
    (
        nombre,
        descripcion,
        horario,
        responsable,
        estado,
        id_servicio
    ))

    conexion.commit()

    return redirect('/servicios')

@app.route('/personal')
def personal():

    if 'rol' not in session:
        return redirect('/login')

    if session['rol'] != 'admin':
        return redirect('/login')

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM personal")

    personal = cursor.fetchall()

    return render_template(
        'personal.html',
        personal=personal
    )

@app.route('/nuevo_personal')
def nuevo_personal():
    return render_template('nuevo_personal.html')

@app.route('/guardar_personal', methods=['POST'])
def guardar_personal():

    nombre = request.form['nombre']
    puesto = request.form['puesto']
    area = request.form['area']
    telefono = request.form['telefono']
    correo = request.form['correo']
    turno = request.form['turno']

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO personal
        (
            nombre,
            puesto,
            area,
            telefono,
            correo,
            turno
        )
        VALUES
        (%s,%s,%s,%s,%s,%s)
    """,
    (
        nombre,
        puesto,
        area,
        telefono,
        correo,
        turno
    ))

    conexion.commit()

    return redirect('/personal')

@app.route('/eliminar_personal/<int:id>')
def eliminar_personal(id):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM personal WHERE id_personal=%s",
        (id,)
    )

    conexion.commit()

    return redirect('/personal')

@app.route('/editar_personal/<int:id>')
def editar_personal(id):

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM personal WHERE id_personal=%s",
        (id,)
    )

    personal = cursor.fetchone()

    return render_template(
        'editar_personal.html',
        personal=personal
    )

@app.route('/actualizar_personal', methods=['POST'])
def actualizar_personal():

    id_personal = request.form['id_personal']

    nombre = request.form['nombre']
    puesto = request.form['puesto']
    area = request.form['area']
    telefono = request.form['telefono']
    correo = request.form['correo']
    turno = request.form['turno']

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
    UPDATE personal
    SET nombre=%s,
        puesto=%s,
        area=%s,
        telefono=%s,
        correo=%s,
        turno=%s
    WHERE id_personal=%s
    """,
    (
        nombre,
        puesto,
        area,
        telefono,
        correo,
        turno,
        id_personal
    ))

    conexion.commit()

    return redirect('/personal')


@app.route('/crear_reporte')
def crear_reporte():

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
    SELECT *
    FROM servicios
    WHERE estado_servicio='Activo'
    """)

    servicios = cursor.fetchall()

    return render_template(
        'crear_reporte.html',
        servicios=servicios
    )

@app.route('/guardar_reporte', methods=['POST'])
def guardar_reporte():

    fecha = datetime.now().date()

    hora = datetime.now().time()

    descripcion = request.form['descripcion']

    ubicacion = request.form['ubicacion']

    prioridad = request.form['prioridad']

    id_servicio = request.form['id_servicio']

    id_usuario = session['id_usuario']

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
    INSERT INTO reportes
    (
    fecha_reporte,
    hora_reporte,
    descripcion,
    ubicacion,
    prioridad,
    id_usuario,
    id_servicio
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s)
    """,
    (
    fecha,
    hora,
    descripcion,
    ubicacion,
    prioridad,
    id_usuario,
    id_servicio
    ))

    conexion.commit()

    return redirect('/mis_reportes')

@app.route('/mis_reportes')
def mis_reportes():

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
    SELECT
    r.*,
    s.nombre_servicio

    FROM reportes r

    INNER JOIN servicios s
    ON r.id_servicio=s.id_servicio

    WHERE r.id_usuario=%s

    ORDER BY r.id_reporte DESC
    """,
    (session['id_usuario'],)
    )

    reportes = cursor.fetchall()

    return render_template(
        'mis_reportes.html',
        reportes=reportes
    )


@app.route('/reportes')
def reportes():

    if 'rol' not in session:
        return redirect('/login')

    if session['rol'] != 'admin':
        return redirect('/login')

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
    SELECT
        r.*,
        u.nombre AS usuario,
        s.nombre_servicio,
        p.nombre AS personal

    FROM reportes r

    INNER JOIN usuarios u
        ON r.id_usuario = u.id_usuario

    INNER JOIN servicios s
        ON r.id_servicio = s.id_servicio

    LEFT JOIN personal p
        ON r.id_personal = p.id_personal

    ORDER BY r.id_reporte DESC
    """)

    reportes = cursor.fetchall()

    return render_template(
        'reportes.html',
        reportes=reportes
    )

@app.route('/gestionar_reporte/<int:id>')
def gestionar_reporte(id):

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM reportes WHERE id_reporte=%s",
        (id,)
    )

    reporte = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM personal"
    )

    personal = cursor.fetchall()

    return render_template(
        'gestionar_reporte.html',
        reporte=reporte,
        personal=personal
    )

@app.route('/actualizar_reporte', methods=['POST'])
def actualizar_reporte():

    id_reporte = request.form['id_reporte']

    estado_nuevo = request.form['estado']

    id_personal = request.form['id_personal']

    observaciones = request.form['observaciones']

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT estado FROM reportes WHERE id_reporte=%s",
        (id_reporte,)
    )

    reporte = cursor.fetchone()

    estado_anterior = reporte['estado']

    cursor.execute("""
    UPDATE reportes
    SET estado=%s,
        id_personal=%s
    WHERE id_reporte=%s
    """,
    (
        estado_nuevo,
        id_personal if id_personal else None,
        id_reporte
    ))

    cursor.execute("""
    INSERT INTO historial_reportes
    (
        id_reporte,
        estado_anterior,
        estado_nuevo,
        fecha_cambio,
        observaciones
    )
    VALUES
    (%s,%s,%s,%s,%s)
    """,
    (
        id_reporte,
        estado_anterior,
        estado_nuevo,
        datetime.now(),
        observaciones
    ))

    conexion.commit()

    return redirect('/reportes')

@app.route('/registro')
def registro():

    return render_template('registro.html')

@app.route('/guardar_registro', methods=['POST'])
def guardar_registro():

    nombre = request.form['nombre']
    correo = request.form['correo']
    password = request.form['password']

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO usuarios
    (nombre, correo, password, rol)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            nombre,
            correo,
            password,
            'usuario'
        )
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)