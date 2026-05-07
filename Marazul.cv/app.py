from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)

# Conexão remota com o banco Neon
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://neondb_owner:npg_cieEP9DmH7gW@ep-gentle-band-al1x6p1q-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS ---

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.Text, nullable=False)

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(10, 2))

class ChatProduto(db.Model):
    __tablename__ = 'chat_produto'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    comprador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    vendedor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    mensagem = db.Column(db.Text, nullable=False)
    enviada_em = db.Column(db.DateTime, server_default=db.func.now())

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/registrar', methods=['POST'])
def registrar():
    dados = request.get_json()
    username = dados.get('username')
    senha = dados.get('password')
    if Usuario.query.filter_by(username=username).first():
        return jsonify({"erro": "Usuario ja existe"}), 400
    novo_usuario = Usuario(username=username, senha_hash=generate_password_hash(senha))
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({"mensagem": f"Usuario {username} criado!"}), 201

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    usuario = Usuario.query.filter_by(username=dados.get('username')).first()
    if not usuario or not check_password_hash(usuario.senha_hash, dados.get('password')):
        return jsonify({"erro": "Credenciais invalidas"}), 401
    return jsonify({"usuario_id": usuario.id, "username": usuario.username}), 200

# --- ROTAS DE PRODUTOS E VITRINE ---

@app.route('/postar_produto', methods=['POST'])
def postar_produto():
    dados = request.get_json()
    novo_p = Produto(
        vendedor_id=dados.get('vendedor_id'),
        titulo=dados.get('titulo'),
        descricao=dados.get('descricao'),
        preco=dados.get('preco')
    )
    db.session.add(novo_p)
    db.session.commit()
    return jsonify({"mensagem": "Produto postado!"}), 201

@app.route('/vitrine', methods=['GET'])
def vitrine():
    produtos = Produto.query.all()
    return jsonify([{
        "id": p.id,
        "titulo": p.titulo,
        "descricao": p.descricao,
        "preco": str(p.preco),
        "vendedor_id": p.vendedor_id
    } for p in produtos]), 200

# --- ROTAS DE CHAT ---

@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    dados = request.get_json()
    nova_msg = ChatProduto(
        produto_id=dados.get('produto_id'),
        comprador_id=dados.get('comprador_id'),
        vendedor_id=dados.get('vendedor_id'),
        mensagem=dados.get('mensagem')
    )
    db.session.add(nova_msg)
    db.session.commit()
    return jsonify({"status": "Mensagem enviada!"}), 201

@app.route('/ler_chat/<int:produto_id>', methods=['GET'])
def ler_chat(produto_id):
    mensagens = ChatProduto.query.filter_by(produto_id=produto_id).all()
    return jsonify([{
        "remetente": m.comprador_id,
        "texto": m.mensagem,
        "data": m.enviada_em
    } for m in mensagens]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
