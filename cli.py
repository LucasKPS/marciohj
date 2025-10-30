
import subprocess
import json
import sys

def execute_command(command):
    """Executa um comando no shell e imprime a saída de forma legível."""
    print(f"\n-> Executando comando...\n")
    try:
        # Usamos o shell=True por conveniência para os comandos curl complexos
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, encoding='utf-8')
        try:
            # Tenta formatar a saída como JSON
            parsed_json = json.loads(process.stdout)
            print("✅ Sucesso! Resposta:")
            # ensure_ascii=False para imprimir acentos corretamente
            print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            # Se não for JSON, imprime como texto normal
            print("✅ Sucesso! Resposta:")
            print(process.stdout)

    except subprocess.CalledProcessError as e:
        print("❌ Erro ao executar o comando:")
        # Tenta formatar a mensagem de erro como JSON
        try:
            parsed_json = json.loads(e.stdout)
            print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
        except (json.JSONDecodeError, TypeError):
            # Se não for JSON, imprime o erro bruto
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
    finally:
        # Pausa para o usuário ler a saída antes de limpar o terminal
        input("\nPressione Enter para continuar...")

def create_user():
    """Solicita dados e cria um novo usuário."""
    print("\n--- Criar Novo Usuário ---")
    name = input("Digite o nome: ")
    email = input("Digite o email: ")
    # Escapando as aspas para o comando shell
    command = f"curl -s -X POST -H \"Content-Type: application/json\" -d '{{\"name\": \"{name}\", \"email\": \"{email}\"}}' http://localhost:5000/users"
    execute_command(command)

def list_users():
    """Lista todos os usuários."""
    print("\n--- Listando Usuários ---")
    command = "curl -s http://localhost:5000/users"
    execute_command(command)

def add_series():
    """Solicita dados e adiciona uma nova série."""
    print("\n--- Adicionar Nova Série ---")
    title = input("Digite o título: ")
    genre = input("Digite o gênero: ")
    rating = input("Digite a avaliação (número): ")
    while not rating.isdigit():
        print("A avaliação deve ser um número.")
        rating = input("Digite a avaliação (número): ")
    command = f"curl -s -X POST -H \"Content-Type: application/json\" -d '{{\"title\": \"{title}\", \"genre\": \"{genre}\", \"rating\": {rating}}}' http://localhost:5000/series"
    execute_command(command)

def list_series():
    """Lista todas as séries."""
    print("\n--- Listando Séries ---")
    command = "curl -s http://localhost:5000/series"
    execute_command(command)

def get_recommendations():
    """Solicita um ID de usuário e obtém recomendações."""
    print("\n--- Obter Recomendações ---")
    user_id = input("Digite o ID do usuário para obter recomendações: ")
    while not user_id.isdigit():
        print("O ID do usuário deve ser um número.")
        user_id = input("Digite o ID do usuário: ")
    command = f"curl -s http://localhost:5000/recommendations/{user_id}"
    execute_command(command)

def main_menu():
    """Exibe o menu principal e processa a entrada do usuário."""
    while True:
        # Limpa o terminal para uma melhor experiência (funciona em Linux/macOS)
        # Para Windows, seria 'cls'
        subprocess.run("clear", shell=True)
        print("========= MENU DE INTERAÇÃO ==========")
        print("Escolha uma opção:")
        print("  1. Criar usuário")
        print("  2. Listar usuários")
        print("  3. Adicionar série")
        print("  4. Listar séries")
        print("  5. Obter recomendações")
        print("  6. Sair")
        print("====================================")
        choice = input("Digite o número da sua escolha: ")

        if choice == '1':
            create_user()
        elif choice == '2':
            list_users()
        elif choice == '3':
            add_series()
        elif choice == '4':
            list_series()
        elif choice == '5':
            get_recommendations()
        elif choice == '6':
            print("Saindo do sistema. Até logo!")
            sys.exit()
        else:
            print("\nOpção inválida. Tente novamente.")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    # Verifica se os serviços estão no ar antes de iniciar o menu
    print("Verificando se os serviços estão no ar...")
    try:
        subprocess.run("curl -s --head http://localhost:5000", shell=True, check=True, capture_output=True)
        main_menu()
    except subprocess.CalledProcessError:
        print("\n============================================================")
        print("❌ ERRO: Não foi possível conectar à API na porta 5000.")
        print("   Por favor, inicie os serviços com o comando 'bash run.sh'")
        print("   em outro terminal antes de executar este script.")
        print("============================================================")
        sys.exit(1)

