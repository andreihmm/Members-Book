import os
from flask import Flask, render_template, request, redirect, url_for, session
from groq import Groq
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader

# Configuração do Cloudinary (NOVA SEÇÃO)
cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
  api_key = os.getenv('CLOUDINARY_API_KEY'),
  api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

app = Flask(__name__)

################

app.secret_key = 'a_sua_chave_secreta_muito_longa_e_aleatoria'

###################


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
GROQ_ENJOY = os.getenv('GROQ_ENJOY')
groq_client = Groq(api_key=GROQ_ENJOY)

MONGO_ENJOY = os.environ.get("MONGO_URI")
mongo_client = MongoClient(MONGO_ENJOY)

if not MONGO_ENJOY:
    mongo_uri = "mongodb://localhost:27017/"

db = mongo_client['Enjoy']

##################################################

# a partir do banco você define as tabelas e opera a partir dessas variáveis
segmentos = db['Segmentos']
classes = db['Classes']
usuarios = db['Usuarios']
usuarios_collection = db['Usuarios']


##################################################



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Pega todos os dados do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('password')
        data_nascimento_str = request.form.get('data_nascimento')
        empresa = request.form.get('empresa')
        
        ############
        classe_do_form = request.form.get('classe')
        classe_capitalizada = classe_do_form.capitalize()
        #########

        ###########
        segmento_do_form = request.form.get('segmento')
        #######

        cargo = request.form.get('cargo')
        data_entrada_str = request.form.get('data_entrada')
        diga_mais_raw = request.form.get('diga_mais')
        
        url_imagem = "" # Define um valor padrão caso não haja imagem

        foto = request.files.get('foto_perfil')

        if foto and foto.filename != '':
            try:
                print(f"Enviando a imagem '{foto.filename}' para o Cloudinary...")
                # Faz o upload do arquivo para o Cloudinary
                upload_result = cloudinary.uploader.upload(foto)
                # Pega a URL segura da imagem
                url_imagem = upload_result.get('secure_url')
                print(f"Upload bem-sucedido! URL: {url_imagem}")
            except Exception as e:
                print(f"Erro no upload para o Cloudinary: {e}")
                # A url_imagem continuará como ""

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
                chat_completion = groq_client.chat.completions.create(
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
        

                # Converte a data de entrada para o formato correto
        data_entrada = None
        if data_entrada_str:
            data_entrada = datetime.datetime.strptime(data_entrada_str, '%Y-%m-%d')
        
        data_nascimento = None
        if data_nascimento_str:
            data_nascimento = datetime.datetime.strptime(data_nascimento_str, '%Y-%m-%d')
            

        classe_doc = classes.find_one({"nome": classe_capitalizada})

        if classe_doc:
            # Se encontrou, atribui o _id do documento ao novo_usuario
            print(f"Atenção: A classe '{classe_capitalizada}' foi encontrada na base de dados.")
        else:
            # Se não encontrou (a busca retornou None), você pode lidar com isso
            # Por exemplo, atribuir uma classe padrão ou registrar o erro
            print(f"Atenção: A classe '{classe_capitalizada}' não foi encontrada na base de dados. O perfil será criado sem uma classe específica.")
            # Você pode optar por deixar o campo de classe vazio ou com um valor padrão
        
        segmento_doc = segmentos.find_one({"nome": segmento_do_form})

        if segmento_doc:
            # Se encontrou, atribui o _id do documento ao novo_usuario
            print(f"Atenção: O segmento '{segmento_doc}' foi encontrada na base de dados.")
        else:
            # Se não encontrou (a busca retornou None), você pode lidar com isso
            # Por exemplo, atribuir uma classe padrão ou registrar o erro
            print(f"Atenção: O segmento '{segmento_doc}' não foi encontrada na base de dados. O perfil será criado sem uma classe específica.")
            # Você pode optar por deixar o campo de classe vazio ou com um valor padrão

        documento_usuario = {
            "nome": nome,
            "email": email,
            "senha": password,
            "data_nascimento": data_nascimento,
            "empresa": empresa,
            "classe": classe_doc["_id"],
            "segmento": segmento_doc["_id"],
            "cargo": cargo,
            "data_entrada": data_entrada,
            "descricao": diga_mais_formatted,  # Salva o texto formatado
            "url_imagem": url_imagem
        }
        
        # 4. Insere o documento no MongoDB
        try:
            usuarios_collection.insert_one(documento_usuario)
            print("Documento inserido no MongoDB com sucesso!")
            
            # Opcional: Redireciona para a página de sucesso
            return "Registro finalizado com sucesso! Dados salvos no banco de dados."
            
        except Exception as e:
            print(f"Erro ao salvar no MongoDB: {e}")
            return "Ocorreu um erro ao salvar os dados. Tente novamente mais tarde."

        # # --- DEBUG AQUI! ---
        # # Imprime o texto original e o texto formatado no console do terminal
        # print("\n--- INFORMAÇÕES DO FORMULÁRIO ---")
        # print(f"Texto Original (diga_mais_raw):\n{diga_mais_raw}\n")
        # print("---")
        # print(f"Texto Formatado (diga_mais_formatted):\n{diga_mais_formatted}\n")
        # print("----------------------------------\n")
        # # -------------------


        # return f"Registro em modo de debug. Verifique o console do terminal para ver a mensagem formatada."


    return render_template('register.html')

@app.route('/')
def index():
    return render_template('splash.html')


# No seu arquivo app.py

# No seu arquivo app.py

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("\n--- INÍCIO DA ROTA DE LOGIN ---")
    
    if request.method == 'POST':
        print("Método da requisição: POST")
        
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        print(f"Dados recebidos do formulário -> Email: {email}, Senha: {senha}")
        
        usuario = usuarios_collection.find_one({'email': email})
        
        # Este print é crucial. Ele mostra se a busca encontrou um usuário ou não.
        print(f"Resultado da busca no banco de dados: {usuario}")

        if usuario:
            print("Usuário encontrado no banco de dados. Verificando a senha...")
            
            if usuario['senha'] == senha:
                print("Verificação de senha: SUCESSO. Redirecionando...")
                session['user_id'] = str(usuario['_id'])
                return redirect(url_for('home'))
            else:
                print("Verificação de senha: FALHOU. Senha incorreta.")
                return render_template('login.html', erro="Email ou senha inválidos.")
        else:
            print("Usuário NÃO encontrado no banco de dados.")
            return render_template('login.html', erro="Email ou senha inválidos.")

    else: # Método é 'GET'
        print("Método da requisição: GET. Renderizando a página de login.")
        
    print("--- FIM DA ROTA DE LOGIN ---\n")
    return render_template('login.html', erro=None)






@app.route('/splash')
def splash():
    return render_template('splash.html')



@app.route('/manifesto')
def manifesto():
    return render_template('manifesto.html')


@app.route('/busca')
def busca():
    try:
        # Busca os 10 usuários mais recentes, ordenando pela data de registro em ordem decrescente
        # O .find() retorna um cursor, que precisa ser convertido para uma lista
        usuarios = list(usuarios_collection.find().sort("data_registro", -1).limit(10))
        
        # Envia a lista de usuários para o template busca.html
        return render_template('busca.html', usuarios=usuarios)
    
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return "Erro ao carregar a página de busca."

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
    # Verifica se o usuário está logado (se o user_id existe na sessão)
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Encontra o usuário no banco de dados usando o ID da sessão
        usuario_logado = usuarios_collection.find_one({"_id": ObjectId(user_id)})
        
        if usuario_logado:
            # Renderiza a página home com as informações do usuário
            return render_template('home.html', usuario=usuario_logado)
        else:
            # Caso o usuário não seja encontrado, redireciona para o login
            return redirect(url_for('login'))
    else:
        # Se não há usuário na sessão, redireciona para a página de login
        return redirect(url_for('login'))


@app.route('/membros')
def membros():
    return render_template('membros.html')

@app.route('/membro')
def membro():
    return render_template('membro.html')



# --- Rota para o Perfil do Usuário ---
@app.route('/perfil/<user_id>')
def perfil(user_id):
    try:
        user_object_id = ObjectId(user_id)
        usuario = usuarios_collection.find_one({"_id": user_object_id})
        
        if not usuario:
            return "Usuário não encontrado.", 404
        
        # Obtém a classe_id do usuário
        classe_id = usuario.get('classe')
        
        # Encontra o nome da classe usando a FK
        classe_doc = classes.find_one({"_id": classe_id})
        classe_nome = classe_doc.get('nome') if classe_doc else 'Não Definida'
        
        #
        segmento_id = usuario.get('segmento')

        # Encontra o nome do segmento usando a FK
        segmento_doc = segmentos.find_one({"_id": segmento_id})
        semento_nome = segmento_doc.get('nome') if segmento_doc else 'Não Definida'
        
        # Agora, determine qual template renderizar
        if classe_id == ObjectId("68c5d5307121e8f8f57359c8"):
            return render_template('perfil_socio.html', usuario=usuario, classe_nome=classe_nome, segmento_nome=semento_nome)
        
        elif classe_id == ObjectId("68c5d5307121e8f8f57359c9"):
            return render_template('perfil_infinity.html', usuario=usuario, classe_nome=classe_nome, segmento_nome=semento_nome)
            
        elif classe_id == ObjectId("68c5d5307121e8f8f57359ca"):
            return render_template('perfil_membro.html', usuario=usuario, classe_nome=classe_nome, segmento_nome=semento_nome)
            
        else:
            return render_template('perfil_padrao.html', usuario=usuario, classe_nome=classe_nome, segmento_nome=semento_nome)

    except Exception as e:
        print(f"Erro ao buscar o perfil do usuário: {e}")
        return "Ocorreu um erro ao carregar o perfil.", 500

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
