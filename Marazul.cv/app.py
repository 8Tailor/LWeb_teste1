import os
import pg8000.native
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Função de conexão com os dados do seu projeto Neon
def conectar():
    return pg8000.native.Connection(
        user="neondb_owner",
        password="COLOQUE_A_SENHA_AQUI", # <--- Pegue a senha na sua Screenshot_20260505-184812.png
        host="ep-gentle-band-a11x6p1q.c-3.eu-central-1.aws.neon.tech",
        database="neondb",
        port=5432,
        ssl_context=True
    )

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    try:
        db = conectar()
        # Esta linha garante que todas as contas apareçam para quem pesquisar
        res = db.run("SELECT username, bio FROM usuarios")
        return jsonify(res)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    # Configuração para rodar na nuvem (Render/Koyeb)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
