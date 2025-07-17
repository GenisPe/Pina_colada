from flask import Flask, request, render_template, render_template_string
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
import os
import smtplib
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_por_defecto')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    verificado = db.Column(db.Boolean, default=False)

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if Usuario.query.filter_by(email=email).first():
            return "Ese correo ya está registrado."

        nuevo_usuario = Usuario(email=email, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        # Generar token
        token = s.dumps(email, salt='email-confirm')
        link = f'http://localhost:5000/confirm/{token}'

        # Enviar correo
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
                subject = 'Verifica tu cuenta'
                body = f'Haz clic en este enlace para verificar tu cuenta:\n{link}'
                mensaje = f'Subject: {subject}\n\n{body}'
                smtp.sendmail(os.getenv('MAIL_USERNAME'), email, mensaje)
        except Exception as e:
            return f"Error al enviar correo: {e}"

        return "Registro exitoso. Revisa tu correo para confirmar tu cuenta."

    return render_template("registro.html")

# Ruta de verificación
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            usuario.verificado = True
            db.session.commit()
            return render_template_string("<h2>¡Correo verificado!</h2><p>Ya puedes iniciar sesión.</p>")
    except:
        return render_template_string("<h2>Enlace inválido o expirado.</h2>")
    
    return "Algo salió mal."

# Crear DB si no existe
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
