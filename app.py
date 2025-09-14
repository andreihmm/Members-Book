import os
from flask import Flask, render_template, request, redirect, url_for
from groq import Groq
from dotenv import load_dotenv

app = Flask(__name__)

# Simulação de dados para a página de chats
chats_mock = [
    {
        "nome": "Lucas Andrade",
        "ultima_mensagem": "Ótimo! Fico no aguardo do seu contato.",
        "horario": "14:30",
        "foto_url": "https://via.placeholder.com/150/0000FF/FFFFFF?text=LA"
    },
    {
        "nome": "Time de Finanças",
        "ultima_mensagem": "A pauta da reunião foi enviada.",
        "horario": "Ontem",
        "foto_url": "https://via.placeholder.com/150/FF0000/FFFFFF?text=TF"
    },
    {
        "nome": "Amanda Oliveira",
        "ultima_mensagem": "Podemos marcar nossa call amanhã?",
        "horario": "22/09",
        "foto_url": "https://via.placeholder.com/150/FFA500/FFFFFF?text=AO"
    },
    {
        "nome": "Grupo de Marketing",
        "ultima_mensagem": "Novo briefing do projeto X foi aprovado!",
        "horario": "21/09",
        "foto_url": "https://via.placeholder.com/150/008000/FFFFFF?text=GM"
    },
    {
        "nome": "Suporte",
        "ultima_mensagem": "Seu pedido de ajuda foi recebido.",
        "horario": "20/09",
        "foto_url": "https://via.placeholder.com/150/800080/FFFFFF?text=S"
    },
]

load_dotenv()
GROQ_FORMATAR = os.getenv('GROQ_ENJOY')
client = Groq(api_key=GROQ_FORMATAR)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        diga_mais_raw = request.form.get('diga_mais')
        nome = request.form.get('nome')
        
        diga_mais_formatted = "" # Inicializa a variável

        prompt_content = (
            f"Você é um redator de perfis profissionais. Sua tarefa é transformar a auto-descrição de um usuário em um "
            f"parágrafo conciso, profissional e inspirador. O texto deve ser escrito na terceira pessoa, utilizando o nome do usuário."
            f"\n\nNome do usuário: {nome}"
            f"\nDescrição do usuário: {diga_mais_raw}"
            f"\n\nExemplo de formato de saída:"
            f"\nLucas Andrade é fundador e CEO da InovaTech Labs, startup de inteligência artificial que desenvolve soluções para automação de processos."
            f"\nÉ palestrante em eventos de tecnologia e mentor de jovens empreendedores. Sua missão é democratizar o acesso à IA para empresas de todos os portes."
        )
        if diga_mais_raw:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": prompt_content

                        },
                        {
                            "role": "user",
                            "content": diga_mais_raw,
                        }
                    ],
                model="llama-3.3-70b-versatile",
                )
                
                diga_mais_formatted = chat_completion.choices[0].message.content
                
            except Exception as e:
                print(f"Erro ao chamar a API Groq: {e}")
                diga_mais_formatted = diga_mais_raw
        
        # --- DEBUG AQUI! ---
        # Imprime o texto original e o texto formatado no console do terminal
        print("\n--- INFORMAÇÕES DO FORMULÁRIO ---")
        print(f"Texto Original (diga_mais_raw):\n{diga_mais_raw}\n")
        print("---")
        print(f"Texto Formatado (diga_mais_formatted):\n{diga_mais_formatted}\n")
        print("----------------------------------\n")
        # -------------------

        # A sua lógica de salvar no banco de dados ficaria aqui

        return f"Registro em modo de debug. Verifique o console do terminal para ver a mensagem formatada."

    return render_template('register.html')

@app.route('/')
def index():
    return render_template('splash.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/splash')
def splash():
    return render_template('splash.html')



@app.route('/manifesto')
def manifesto():
    return render_template('manifesto.html')

@app.route('/busca')
def busca():
    return render_template('busca.html')

chats_mock = [
    {
        "id": 1,
        "nome": "Lucas Andrade",
        "ultima_mensagem": "Ótimo! Fico no aguardo do seu contato.",
        "horario": "14:30",
        "foto_url": "https://via.placeholder.com/150/0000FF/FFFFFF?text=LA"
    },
    {
        "id": 2,
        "nome": "Amanda Oliveira",
        "ultima_mensagem": "Podemos marcar nossa call amanhã?",
        "horario": "22/09",
        "foto_url": "https://via.placeholder.com/150/FFA500/FFFFFF?text=AO"
    }
]

# Simulação de dados para uma conversa específica
conversas_mock = {
    1: [
        {"remetente": "eu", "texto": "Olá, Lucas! Tudo bem?"},
        {"remetente": "Lucas Andrade", "texto": "Tudo sim! Agradeço o contato."},
        {"remetente": "eu", "texto": "Gostaria de falar sobre sua experiência com IA."},
    ],
    2: [
        {"remetente": "eu", "texto": "Oi, Amanda! Vi seu perfil na plataforma."},
        {"remetente": "Amanda Oliveira", "texto": "Olá! Que bom que gostou. Em que posso ajudar?"},
    ]
}

@app.route('/chat')
def chat():
    return render_template('chat.html', chats=chats_mock)

@app.route('/conversa/<int:user_id>')
def conversation(user_id):
    # Encontra o usuário correspondente ao ID
    usuario = next((chat for chat in chats_mock if chat['id'] == user_id), None)
    
    # Encontra as mensagens para a conversa
    mensagens = conversas_mock.get(user_id, [])

    if usuario:
        return render_template('conversa.html', usuario=usuario, mensagens=mensagens)
    else:
        # Retorna uma mensagem de erro ou redireciona
        return "Usuário não encontrado.", 404

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/membros')
def membros():
    return render_template('membros.html')

@app.route('/membro')
def membro():
    return render_template('membro.html')

if __name__ == "__main__":
    app.run(debug=True)






















# from flask import Flask, render_template, redirect, url_for, request

# app = Flask(__name__)
# @app.route('/')
# def index():
#     return render_template('index.html') 

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         return redirect(url_for('home'))
#     return render_template('login.html')

# # Rota de registro (POST para processar o formulário)
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']
#         # Aqui você salvaria o usuário em banco ou memória
#         return redirect(url_for('login'))
#     return render_template('register.html')

# # Rota de home
# @app.route('/home')
# def home():
#     return render_template('home.html')

# # Rota de home
# @app.route('/membros')
# def membros():
#     return render_template('membros.html')

# @app.route('/membro')
# def membro():
#     return render_template('membro.html')

# if __name__ == "__main__":
#     app.run(debug=True)
