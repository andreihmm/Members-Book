from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # necessário para sessões

# Usuários temporários (apenas para protótipo)
USUARIOS = {
    "teste": "1234"
}

# === Splash Screen ===
@app.route('/')
def splash():
    return render_template('splash.html')  # sua tela de carregamento

# === Login ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Verifica usuário (aqui só protótipo)
        if username in USUARIOS and USUARIOS[username] == password:
            session['usuario'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', erro="Usuário ou senha inválidos")
    return render_template('login.html')

# === Logout ===
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# === Registro ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Aqui você processaria o cadastro
        return redirect(url_for('login'))
    return render_template('register.html')

# === Home ===
@app.route('/home')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# === Lista de membros ===
@app.route('/membros')
def membros():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('membros.html')

# === Página de membro individual ===
@app.route('/membro/<int:membro_id>')
def membro(membro_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    # Aqui você buscaria os dados do membro pelo ID
    return render_template('membro.html', membro_id=membro_id)

if __name__ == "__main__":
    app.run(debug=True)
