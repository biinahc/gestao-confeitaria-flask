from waitress import serve
from app import app

if __name__ == "__main__":
    print("===================================================")
    print("Servidor de produção iniciado!")
    # Mensagem atualizada para a nova porta
    print("Acesse o site no seu navegador em: http://localhost:8080")
    print("Para parar o servidor, pressione Ctrl+C")
    print("===================================================")
    # Alteração da porta de 5000 para 8080
    serve(app, host="0.0.0.0", port=8080)