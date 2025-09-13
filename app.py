from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return redirect(url_for('home'))
    return render_template('login.html')

# Rota de registro (POST para processar o formulário)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        # Aqui você salvaria o usuário em banco ou memória
        return redirect(url_for('login'))
    return render_template('register.html')

# Rota de home
@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
