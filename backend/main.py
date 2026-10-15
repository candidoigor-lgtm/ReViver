"""Ponto de entrada alternativo para executar a API ReViver."""
try:
    from .app import app
except ImportError:
    from app import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
