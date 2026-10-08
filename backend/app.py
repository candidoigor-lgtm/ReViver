import os
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

try:
    from cliente_ollama import perguntar_ollama
except Exception:
    perguntar_ollama = None

app = Flask(__name__)
CORS(app)

BASE = Path(__file__).resolve().parent
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/reviver",
)


def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def ensure_services_table():
    sql = """
    CREATE SCHEMA IF NOT EXISTS apoio;
    CREATE TABLE IF NOT EXISTS apoio.servicos_apoio (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(150) NOT NULL,
        descricao TEXT,
        endereco VARCHAR(250),
        cidade VARCHAR(80),
        estado CHAR(2),
        latitude NUMERIC(10,7),
        longitude NUMERIC(10,7),
        telefone VARCHAR(30),
        atende_urgencia BOOLEAN NOT NULL DEFAULT FALSE,
        ativo BOOLEAN NOT NULL DEFAULT TRUE
    );
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def user_id_from_request():
    raw = request.headers.get("X-Usuario-ID")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


@app.get("/")
def home():
    return jsonify({"projeto": "ReViver", "status": "online"})


@app.get("/api/health")
def health():
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok")
                cur.fetchone()
        return jsonify({"status": "ok", "database": "conectado"})
    except Exception as exc:
        return jsonify({"status": "erro", "database": "desconectado", "erro": str(exc)}), 503


@app.post("/api/usuarios")
def criar_usuario():
    data = request.get_json(silent=True) or {}
    nome = str(data.get("nome_exibicao", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    senha = str(data.get("senha", ""))

    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios."}), 400
    if len(senha) < 6:
        return jsonify({"erro": "A senha deve ter pelo menos 6 caracteres."}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO apoio.usuarios (nome_exibicao, email, senha_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id, nome_exibicao, email, criado_em, atualizado_em
                    """,
                    (nome, email, generate_password_hash(senha)),
                )
                usuario = cur.fetchone()
                cur.execute(
                    "INSERT INTO apoio.perfis (usuario_id) VALUES (%s)",
                    (usuario["id"],),
                )
        return jsonify({"mensagem": "Usuário criado com sucesso.", "usuario": usuario}), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"erro": "Este email já está cadastrado."}), 409
    except Exception as exc:
        return jsonify({"erro": str(exc)}), 500


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    senha = str(data.get("senha", ""))

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios."}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome_exibicao, email, senha_hash, ativo FROM apoio.usuarios WHERE email=%s",
                (email,),
            )
            usuario = cur.fetchone()

    if not usuario or not usuario["ativo"] or not check_password_hash(usuario["senha_hash"], senha):
        return jsonify({"erro": "Email ou senha incorretos."}), 401

    usuario.pop("senha_hash", None)
    return jsonify({"mensagem": "Login realizado com sucesso.", "usuario": usuario})


@app.get("/api/usuarios")
def listar_usuarios():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome_exibicao, email, papel, ativo, criado_em FROM apoio.usuarios ORDER BY id")
            return jsonify(cur.fetchall())


@app.get("/api/perfis/<int:usuario_id>")
def obter_perfil(usuario_id):
    if user_id_from_request() != usuario_id:
        return jsonify({"erro": "Usuário não autorizado."}), 401

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.nome_exibicao, u.email, p.ano_nascimento, p.cidade,
                       p.estado, p.substancias_usadas, p.estagio_recuperacao,
                       p.iniciou_recuperacao_em
                FROM apoio.usuarios u
                LEFT JOIN apoio.perfis p ON p.usuario_id = u.id
                WHERE u.id = %s
                """,
                (usuario_id,),
            )
            perfil = cur.fetchone()

    if not perfil:
        return jsonify({"erro": "Usuário não encontrado."}), 404
    return jsonify(perfil)


@app.post("/api/perfis")
def salvar_perfil():
    data = request.get_json(silent=True) or {}
    usuario_id = user_id_from_request() or data.get("usuario_id")
    try:
        usuario_id = int(usuario_id)
    except (TypeError, ValueError):
        return jsonify({"erro": "Informe um usuário válido."}), 400

    if user_id_from_request() != usuario_id:
        return jsonify({"erro": "Usuário não autorizado."}), 401

    idade = data.get("idade")
    ano_nascimento = None
    if idade not in (None, ""):
        try:
            ano_nascimento = __import__("datetime").date.today().year - int(idade)
        except (TypeError, ValueError):
            return jsonify({"erro": "Idade inválida."}), 400

    substancias = data.get("substancias_usadas", [])
    if isinstance(substancias, str):
        substancias = [substancias]

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE apoio.usuarios
                SET nome_exibicao = COALESCE(%s, nome_exibicao), atualizado_em = now()
                WHERE id = %s
                """,
                (data.get("nome_exibicao"), usuario_id),
            )
            cur.execute(
                """
                INSERT INTO apoio.perfis
                    (usuario_id, ano_nascimento, cidade, estado, substancias_usadas, estagio_recuperacao)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (usuario_id) DO UPDATE SET
                    ano_nascimento = EXCLUDED.ano_nascimento,
                    cidade = EXCLUDED.cidade,
                    estado = EXCLUDED.estado,
                    substancias_usadas = EXCLUDED.substancias_usadas,
                    estagio_recuperacao = EXCLUDED.estagio_recuperacao
                RETURNING usuario_id
                """,
                (
                    usuario_id,
                    ano_nascimento,
                    data.get("cidade"),
                    data.get("estado"),
                    substancias,
                    data.get("estagio_recuperacao") or None,
                ),
            )
    return jsonify({"mensagem": "Dados salvos com sucesso."})


@app.post("/api/chats")
def criar_chat():
    usuario_id = user_id_from_request()
    if not usuario_id:
        return jsonify({"erro": "Informe X-Usuario-ID."}), 401
    data = request.get_json(silent=True) or {}
    modelo = str(data.get("modelo", os.getenv("OLLAMA_MODEL", "llama3.2")))

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO apoio.sessoes_chat (usuario_id, modelo) VALUES (%s, %s) RETURNING id, modelo, iniciada_em",
                (usuario_id, modelo),
            )
            return jsonify(cur.fetchone()), 201


@app.get("/api/chats")
def listar_chats():
    usuario_id = user_id_from_request()
    if not usuario_id:
        return jsonify({"erro": "Informe X-Usuario-ID."}), 401
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, modelo, iniciada_em, encerrada_em, sinalizada, resumo_contexto
                FROM apoio.sessoes_chat
                WHERE usuario_id=%s ORDER BY iniciada_em DESC
                """,
                (usuario_id,),
            )
            return jsonify(cur.fetchall())


@app.get("/api/chats/<int:chat_id>/mensagens")
def listar_mensagens(chat_id):
    usuario_id = user_id_from_request()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT usuario_id FROM apoio.sessoes_chat WHERE id=%s", (chat_id,))
            chat = cur.fetchone()
            if not chat or chat["usuario_id"] != usuario_id:
                return jsonify({"erro": "Conversa não encontrada."}), 404
            cur.execute(
                "SELECT id, remetente, conteudo, criada_em FROM apoio.mensagens WHERE sessao_id=%s ORDER BY criada_em",
                (chat_id,),
            )
            return jsonify(cur.fetchall())


def responder_chat(mensagem, contexto=""):
    if perguntar_ollama:
        try:
            return perguntar_ollama(mensagem, contexto)
        except Exception:
            pass
    return (
        "Entendi. Posso ajudar com informações gerais sobre o ReViver, mostrar serviços de apoio "
        "e orientar você a procurar um profissional de saúde quando necessário."
    )


@app.post("/api/chats/<int:chat_id>/mensagens")
def enviar_mensagem(chat_id):
    usuario_id = user_id_from_request()
    data = request.get_json(silent=True) or {}
    mensagem = str(data.get("conteudo", "")).strip()
    if not mensagem:
        return jsonify({"erro": "Mensagem vazia."}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT usuario_id, modelo FROM apoio.sessoes_chat WHERE id=%s", (chat_id,))
            chat = cur.fetchone()
            if not chat or chat["usuario_id"] != usuario_id:
                return jsonify({"erro": "Conversa não encontrada."}), 404

            cur.execute(
                "INSERT INTO apoio.mensagens (sessao_id, remetente, conteudo) VALUES (%s, 'usuario', %s) RETURNING id, remetente, conteudo, criada_em",
                (chat_id, mensagem),
            )
            usuario_msg = cur.fetchone()
            resposta = responder_chat(mensagem, "ReViver: apoio complementar; não substitui profissionais de saúde.")
            cur.execute(
                "INSERT INTO apoio.mensagens (sessao_id, remetente, conteudo) VALUES (%s, 'assistente', %s) RETURNING id, remetente, conteudo, criada_em",
                (chat_id, resposta),
            )
            assistente_msg = cur.fetchone()

    return jsonify({"usuario": usuario_msg, "assistente": assistente_msg})


@app.get("/api/servicos")
def listar_servicos():
    try:
        ensure_services_table()
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, nome, descricao, endereco, cidade, estado,
                           latitude, longitude, telefone, atende_urgencia
                    FROM apoio.servicos_apoio WHERE ativo=TRUE ORDER BY nome
                    """
                )
                return jsonify(cur.fetchall())
    except Exception as exc:
        return jsonify({"erro": str(exc)}), 500


@app.post("/api/servicos")
def criar_servico():
    data = request.get_json(silent=True) or {}
    if not data.get("nome"):
        return jsonify({"erro": "Nome do serviço é obrigatório."}), 400
    try:
        ensure_services_table()
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO apoio.servicos_apoio
                    (nome, descricao, endereco, cidade, estado, latitude, longitude, telefone, atende_urgencia)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING *
                    """,
                    (
                        data.get("nome"), data.get("descricao"), data.get("endereco"),
                        data.get("cidade"), data.get("estado"), data.get("latitude"),
                        data.get("longitude"), data.get("telefone"), bool(data.get("atende_urgencia", False)),
                    ),
                )
                return jsonify(cur.fetchone()), 201
    except Exception as exc:
        return jsonify({"erro": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
