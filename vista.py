from email.message import EmailMessage
import smtplib
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from conexion import crear, get_db
from modelo import base, Registro, RecursoLegales,GestionCasos
from shemas import Usuario, Login
from shemas import RecursosLegales as recursos
from shemas import GestionCasos as casos
import bcrypt
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Configura CORS
origins = [
    "http://localhost:5173",  # Origen de tu frontend (Vue/React)
    "http://127.0.0.1:5173",  # Alternativa
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],       # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],       # Permite todos los encabezados
)

base.metadata.create_all(bind=crear)

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario: str, nombre_usuario: str):
    remitente = "juricoconsultorio@gmail.com"
    # Usa la contraseña de aplicación que generaste en lugar de tu contraseña normal
    contraseña = "rict atrp aolk grlk" 
    
    # Crear el mensaje
    mensaje = MIMEMultipart()
    mensaje['Subject'] = 'Registro exitoso en el Consultorio Jurídico'
    mensaje['From'] = remitente
    mensaje['To'] = destinatario

    # Contenido HTML con más estilos y diseño
    html_contenido = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    -webkit-text-size-adjust: none;
                    -ms-text-size-adjust: none;
                }}
                .email-container {{
                    width: 100%;
                    padding: 20px 0;
                    background-color: #f4f4f4;
                }}
                .email-body {{
                    width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                }}
                h2 {{
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 15px;
                }}
                p {{
                    font-size: 16px;
                    color: #7f8c8d;
                    line-height: 1.5;
                    margin-bottom: 15px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    font-size: 16px;
                    color: #fff;
                    background-color: #3498db;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 20px;
                }}
                .button:hover {{
                    background-color: #2980b9;
                }}
                .footer {{
                    font-size: 12px;
                    color: #95a5a6;
                    text-align: center;
                    margin-top: 30px;
                }}
                @media (max-width: 600px) {{
                    .email-body {{
                        width: 100% !important;
                        padding: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-body">
                    <h2>¡Hola {nombre_usuario}!</h2>
                    <p>Gracias por registrarte en el <strong>Consultorio Jurídico</strong>. Tu cuenta ha sido creada exitosamente.</p>
                    <p>Estamos listos para ayudarte en lo que necesites. Si tienes alguna pregunta, no dudes en ponerte en contacto con nosotros.</p>
                    <a href="https://www.unicolmayor.edu.co/" class="button">Visitar nuestro sitio</a>
                    <div class="footer">
                        <p>Este es un mensaje automático, por favor no respondas.</p>
                        <p>&copy; 2024 Consultorio Jurídico. Todos los derechos reservados.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    
    # Agregar el contenido HTML al mensaje
    mensaje.attach(MIMEText(html_contenido, 'html', 'utf-8'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()  # Inicia la conexión segura con TLS
            servidor.login(remitente, contraseña)
            servidor.send_message(mensaje)
            print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

@app.post('/insertar', response_model=Usuario)
async def registrar_cliente(clientemodel: Usuario, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(clientemodel.password.encode('utf-8'), bcrypt.gensalt())
    datos = Registro(**clientemodel.dict())
    datos.password = hashed_password.decode('utf-8')
    db.add(datos)
    db.commit()
    db.refresh(datos)
    
    print(f"Enviando correo a: {clientemodel.correo}")
    
    # Enviar correo al usuario con estilo HTML
    enviar_correo(clientemodel.correo, clientemodel.nombre)
    
    return datos

#Recuperacion de contraseña o envio de credenciales-------------------------------------------

import secrets

def generar_token():
    return secrets.token_urlsafe(16)



def enviar_correo_credenciales(destinatario, nombre, token):
    remitente = "juricoconsultorio@gmail.com"
    contraseña = "rict atrp aolk grlk"
    
    mensaje = MIMEMultipart()
    mensaje['Subject'] = 'Restablecimiento de Contraseña'
    mensaje['From'] = remitente
    mensaje['To'] = destinatario

    enlace = f"http://localhost:5173/restablecerContrasena?token={token}"
    html_contenido = f"""
    <html>
    <body>
        <h2>Hola, {nombre}</h2>
        <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
        <p><a href="{enlace}">Restablecer Contraseña</a></p>
        <p>Si no solicitaste este cambio, ignora este correo.</p>
    </body>
    </html>
    """
    
    mensaje.attach(MIMEText(html_contenido, 'html', 'utf-8'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()
            servidor.login(remitente, contraseña)
            servidor.send_message(mensaje)
            print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        

class EmailSchema(BaseModel):
    email: EmailStr


@app.post("/enviarcredenciales")
async def enviar_credenciales(request: EmailSchema, db: Session = Depends(get_db)):
    db_user = db.query(Registro).filter(Registro.correo == request.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    token = generar_token()
    db_user.token = token  # Guarda el token en el usuario
    db.commit()  # Actualiza la base de datos

    enviar_correo_credenciales(db_user.correo, db_user.nombre, token)
    return {"detail": "Correo enviado con éxito"}


class ResetPasswordRequest(BaseModel):
    token: str
    nueva_contraseña: str  # Asegúrate de que coincida con el nombre del campo enviado

@app.post("/restablecer-contrasena")
async def restablecer_contraseña(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(Registro).filter(Registro.token == request.token).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Token no válido o expirado")

    hashed_password = bcrypt.hashpw(request.nueva_contraseña.encode('utf-8'), bcrypt.gensalt())
    db_user.password = hashed_password.decode('utf-8')
    db.commit()
    return {"detail": "Contraseña restablecida con éxito"}
#--------------------------------------------------------------------------------------



@app.delete("/eliminar/{documento}")
async def eliminar_cliente(documento: int, db: Session = Depends(get_db)):
    datos_cliente = db.query(Registro).filter(Registro.documento == documento).first()

    if datos_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(datos_cliente)
    db.commit()
    return {"detail": "Cliente eliminado con éxito"}

@app.get('/consultarCliente', response_model=list[Usuario])
async def Consultar_cliente(db: Session = Depends(get_db)):
    datos_cliente = db.query(Registro).all()
    return datos_cliente


@app.put("/modificar/{documento}", response_model=Usuario)
async def modificar_cliente(documento: int, clientemodel: Usuario, db: Session = Depends(get_db)):
    datos_cliente = db.query(Registro).filter(Registro.documento == documento).first()

    if datos_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Actualiza todos los campos del cliente
    for key, value in clientemodel.dict().items():
        setattr(datos_cliente, key, value)

    try:
        db.commit()  # Guarda los cambios en la base de datos
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))  # Maneja errores de commit

    return datos_cliente  # Retorna los datos del cliente modificado




@app.get('/clientes/{documento}', response_model=Usuario)
async def consultar_cliente(documento: int, db: Session = Depends(get_db)):
    datos_cliente = db.query(Registro).filter(Registro.documento == documento).first()
    if datos_cliente is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return datos_cliente

@app.get("/cliente/documento/", response_model=list[int])
async def getdocumentoCliente(db: Session = Depends(get_db)):
    documento = db.query(Registro.documento).all()
    return [doc[0] for doc in documento]



@app.post("/login")
async def login(user: Login, db: Session = Depends(get_db)):
    db_user = db.query(Registro).filter(Registro.documento == user.documento).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Usuario no existe")
    
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    return {
        "mensaje": "Inicio de sesión exitoso",
        "nombre": db_user.nombre,
        "rol": db_user.rol
    }


@app.post('/insertarRecurso', response_model=recursos)
async def registrar_Recurso(recur: recursos, db: Session = Depends(get_db)):
    datos = RecursoLegales(**recur.dict())
    db.add(datos)
    db.commit()
    db.refresh(datos)
    return datos

@app.get('/consultarRecurso',response_model=list[recursos])
async def Consultar_cliente(db:Session=Depends(get_db)):
    datos_cliente=db.query(RecursoLegales).all()
    return datos_cliente


@app.delete('/eliminarRecurso/{id}', response_model=recursos)
async def eliminar_recurso(id: int, db: Session = Depends(get_db)):
    recurso = db.query(RecursoLegales).filter(RecursoLegales.id_documento == id).first()
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    
    db.delete(recurso)
    db.commit()
    return recurso

@app.put('/actualizarRecurso/{id}', response_model=recursos)
async def actualizar_recurso(id: int, recur: recursos, db: Session = Depends(get_db)):
    recurso = db.query(RecursoLegales).filter(RecursoLegales.id_documento == id).first()

    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")

    recurso.nombre_recurso = recur.nombre_recurso
    recurso.descripcion = recur.descripcion
    recurso.tipo = recur.tipo
    recurso.Url = recur.Url

    
    db.commit()
    db.refresh(recurso)

    return recurso

    #  --------------------------------- GESTION DE CASOS ----------------------------------------------
@app.post('/insertar_caso', response_model=casos)
async def registrar_Recurso(casos: casos, db: Session = Depends(get_db)):
    datos = GestionCasos(**casos.dict())
    db.add(datos)
    db.commit()
    db.refresh(datos)
    return datos

@app.get('/consultar_lista_casos',response_model=list[casos])
async def Consultar_cliente(db:Session=Depends(get_db)):
    datos_cliente=db.query(GestionCasos).all()
    return datos_cliente

@app.delete('/eliminar_casos/{id}', response_model=casos)
async def eliminar_casos(id:str, db: Session = Depends(get_db)):
    recurso = db.query(GestionCasos).filter(GestionCasos.numero_caso == id).first()
    if not recurso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    
    db.delete(recurso)
    db.commit()
    return recurso


from sqlalchemy import or_

@app.get('/caso_filtter/{documento}', response_model=list[casos])
async def consultar_cliente(documento: str, db: Session = Depends(get_db)):
    # Comparamos primero con documento_usuario y luego con tipo_caso, usando OR
    datos_cliente = db.query(GestionCasos).filter(
        or_(
            GestionCasos.documento_usuario == documento,
            GestionCasos.tipo_caso == documento
        )
    ).all()  # Usamos .all() para obtener todos los registros que cumplan la condición

    if not datos_cliente:  # Si no hay datos, devolvemos un 404
        raise HTTPException(status_code=404, detail="dato no encontrado")
    
    return datos_cliente  # Retornamos




