from flask import Flask, request, render_template_string
import smtplib
from itsdangerous import URLSafeTimedSerializer
from flask_sqlalchemy import SQLAlchemy

# Configuración inicial de la aplicación
app = Flask(__name__)

# Clave secreta para generar tokens seguros
app.config['SECRET_KEY'] = 'clave_secreta'

# Configuración de base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

# Serializador para crear tokens seguros de verificación
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Modelo de base de datos para los usuarios
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    verificado = db.Column(db.Boolean, default=False)

# Ruta para procesar el formulario de registro
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    # Verificar si el correo ya existe
    if Usuario.query.filter_by(email=email).first():
        return "Ese correo ya está registrado."

    # Guardar nuevo usuario en la base de datos (aún no verificado)
    nuevo_usuario = Usuario(email=email, password=password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Crear token único para verificación
    token = s.dumps(email, salt='email-confirm')
    link = f'http://localhost:5000/confirm/{token}'

    # Enviar correo de verificación
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('TUCORREO@gmail.com', 'TU_CLAVE_APP')  # Cambia esto por tu info real
            mensaje = f'Subject: Verifica tu cuenta\n\nHaz clic en el siguiente enlace para verificar tu cuenta:\n{link}'
            smtp.sendmail('TUCORREO@gmail.com', email, mensaje)
    except Exception as e:
        return f"Error al enviar correo: {e}"

    return "Registro exitoso. Revisa tu correo electrónico para confirmar tu cuenta."

# Ruta para confirmar el correo electrónico
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        # Verificar token y obtener el email original
        email = s.loads(token, salt='email-confirm', max_age=3600)  # válido por 1 hora
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            usuario.verificado = True
            db.session.commit()
            return render_template_string("<h2>¡Correo verificado!</h2><p>Ahora puedes iniciar sesión.</p>")
    except:
        return render_template_string("<h2>Enlace inválido o expirado.</h2>")

    return "Algo salió mal."

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# Ejecutar el servidor Flask en modo desarrollo
if __name__ == '__main__':
    app.run(debug=True)
