from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Usuario, Jugador, Equipo, JugadorEquipo
import os
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
instance_path = os.path.join(BASE_DIR, 'instance')
database_path = os.path.join(instance_path, 'database.db')

app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


os.makedirs(instance_path, exist_ok=True)

# Inicialización de extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('index'))
        
        flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    
    logger.info(f"Intento de registro para usuario: {username}")
    
    try:
        
        if not username or not password or not password_confirm:
            flash('Por favor completa todos los campos', 'danger')
            return redirect(url_for('login'))
            
        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('login'))
        
        # Verificar si el usuario ya existe
        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso', 'danger')
            return redirect(url_for('login'))
        
        
        nuevo_usuario = Usuario(username=username)
        nuevo_usuario.set_password(password)
        
        # Intentar guardar en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        logger.info(f"Usuario {username} creado exitosamente")
        
        # Iniciar sesión automáticamente
        login_user(nuevo_usuario)
        flash('¡Registro exitoso! Bienvenido.', 'success')
        return redirect(url_for('index'))
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en el registro: {str(e)}")
        flash('Error en el registro. Por favor intenta nuevamente.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Rutas de la API
@app.route('/api/jugadores')
@login_required
def get_jugadores():
    jugadores = Jugador.query.all()
    return jsonify([{
        'id': j.id,
        'nombre': j.nombre,
        'equipo': j.equipo,
        'posicion': j.posicion,
        'edad': j.edad,
        'altura': j.altura,
        'puntos_por_partido': j.puntos_por_partido
    } for j in jugadores])

@app.route('/api/jugadores/<int:id>')
@login_required
def get_jugador(id):
    jugador = Jugador.query.get_or_404(id)
    return jsonify({
        'id': jugador.id,
        'nombre': jugador.nombre,
        'equipo': jugador.equipo,
        'posicion': jugador.posicion,
        'edad': jugador.edad,
        'altura': jugador.altura,
        'universidad': jugador.universidad,
        'pais': jugador.pais,
        'partidos_jugados': jugador.partidos_jugados,
        'puntos_por_partido': jugador.puntos_por_partido,
        'rebotes_por_partido': jugador.rebotes_por_partido,
        'asistencias_por_partido': jugador.asistencias_por_partido
    })

@app.route('/api/jugadores_por_posicion/<posicion>')
@login_required
def get_jugadores_por_posicion(posicion):
    jugadores = Jugador.query.filter_by(posicion=posicion).all()
    return jsonify([{
        'id': j.id,
        'nombre': j.nombre,
        'equipo': j.equipo,
        'posicion': j.posicion,
        'puntos_por_partido': j.puntos_por_partido,
        'rebotes_por_partido': j.rebotes_por_partido,
        'asistencias_por_partido': j.asistencias_por_partido
    } for j in jugadores])

@app.route('/api/crear_equipo', methods=['POST'])
@login_required
def crear_equipo():
    try:
        data = request.get_json()
        tipo_equipo = data.get('tipo')
        jugadores_ids = data.get('jugadores')
        
        equipo = Equipo(
            usuario_id=current_user.id,
            tipo=tipo_equipo
        )
        db.session.add(equipo)
        db.session.flush()
        
        for jugador_id in jugadores_ids:
            jugador_equipo = JugadorEquipo(
                equipo_id=equipo.id,
                jugador_id=jugador_id
            )
            db.session.add(jugador_equipo)
        
        db.session.commit()
        return jsonify({'success': True, 'equipo_id': equipo.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        logger.info("Base de datos inicializada")
        
    app.run(debug=True)