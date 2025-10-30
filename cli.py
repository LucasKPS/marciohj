
import subprocess
import json
import sys
import os

# URL base da nossa API Gateway
API_URL = "http://localhost:5000"

def clear_screen():
    """Limpa o terminal (funciona em Windows, macOS e Linux)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def execute_request(method, endpoint, data=None, silent=False):
    """Constrói e executa um comando cURL, processa e retorna a resposta."""
    headers = "-H \"Content-Type: application/json\""
    data_str = f"-d '{json.dumps(data)}'" if data else ""
    command = f"curl -s -X {method} {headers} {data_str} {API_URL}{endpoint}"

    if not silent:
        print(f"\n-> Executando...\n")

    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, encoding='utf-8')
        response_json = json.loads(process.stdout)
        if not silent:
            print("✅ Sucesso! Resposta:")
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        return response_json

    except subprocess.CalledProcessError as e:
        if not silent:
            print("❌ Erro na requisição:")
            try:
                error_json = json.loads(e.stdout)
                print(json.dumps(error_json, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print("Não foi possível decodificar a resposta de erro.")
                print("Saída bruta:", e.stdout)
        # Retorna o erro como JSON se possível, para que a lógica do app possa usá-lo
        return json.loads(e.stdout) if e.stdout and e.stdout.strip().startswith('{') else None
    except json.JSONDecodeError:
        if not silent:
            print("❌ Erro: Não foi possível decodificar a resposta do servidor.")
        return None

def wait_for_enter():
    input("\nPressione Enter para continuar...")

# --- Funções do Menu ---

def create_user():
    clear_screen()
    print("--- Criar Novo Usuário ---")
    name = input("Digite o nome: ")
    email = input("Digite o email: ")
    execute_request("POST", "/users", data={"name": name, "email": email})
    wait_for_enter()

def list_users():
    clear_screen()
    print("--- Listando Usuários ---")
    execute_request("GET", "/users")
    wait_for_enter()

def add_series():
    clear_screen()
    print("--- Adicionar Nova Série ---")
    title = input("Digite o título: ")
    genre = input("Digite o gênero: ")
    rating_str = input("Digite a avaliação inicial (1-5): ")
    while not rating_str.isdigit() or not 1 <= int(rating_str) <= 5:
        rating_str = input("Inválido. Digite uma avaliação de 1 a 5: ")
    execute_request("POST", "/series", data={"title": title, "genre": genre, "rating": int(rating_str)})
    wait_for_enter()

def list_series():
    clear_screen()
    print("--- Listando Séries ---")
    execute_request("GET", "/series")
    wait_for_enter()

def recommend_by_genre():
    """Recomenda uma série com base em um gênero fornecido pelo usuário."""
    clear_screen()
    print("--- Recomendar Série por Gênero ---")
    genre_to_find = input("Digite o gênero que você gostaria de ver (ex: Comédia, Ação): ")

    if not genre_to_find:
        print("\nO gênero não pode ser vazio.")
        wait_for_enter()
        return

    # Usa o novo endpoint da API para obter a recomendação, de forma silenciosa
    recommendations = execute_request("GET", f"/recommendations/genre/{genre_to_find}", silent=True)

    if recommendations and isinstance(recommendations, list):
        # A API retorna uma lista ordenada, então a melhor recomendação é a primeira.
        best_recommendation = recommendations[0]
        clear_screen()
        print("--- Recomendação para você! ---")
        print(f"Baseado no seu interesse por '{genre_to_find}', recomendamos a seguinte série:")
        print(json.dumps(best_recommendation, indent=2, ensure_ascii=False))
    else:
        # Se a resposta for um erro (dicionário com 'error' ou 'message') ou uma lista vazia
        print(f"\nNão foi possível encontrar uma recomendação para o gênero '{genre_to_find}'.")
        # Vamos buscar os gêneros disponíveis para ajudar o usuário
        all_series = execute_request("GET", "/series", silent=True)
        if all_series and isinstance(all_series, list):
             genres = sorted(list(set(s['genre'] for s in all_series)))
             print("Gêneros disponíveis: " + ", ".join(genres))

    wait_for_enter()

def main_menu():
    """Exibe o menu principal e processa a entrada do usuário."""
    while True:
        clear_screen()
        print("========= MENU DE INTERAÇÃO ==========")
        print("  1. Criar usuário")
        print("  2. Listar usuários")
        print("  3. Adicionar série")
        print("  4. Listar séries")
        print("  5. Obter recomendação por gênero")
        print("------------------------------------")
        print("  6. Sair")
        print("====================================")
        choice = input("Digite o número da sua escolha: ")

        actions = {
            '1': create_user,
            '2': list_users,
            '3': add_series,
            '4': list_series,
            '5': recommend_by_genre, # Aponta para a nova função
            '6': lambda: sys.exit("Saindo do sistema. Até logo!")
        }
        
        action = actions.get(choice)
        if action:
            action()
        else:
            print("\nOpção inválida. Tente novamente.")
            wait_for_enter()

if __name__ == "__main__":
    print("Verificando se a API Gateway está no ar...")
    try:
        # Verifica se a raiz da API responde antes de iniciar o menu
        subprocess.run(f"curl -s --head {API_URL}", shell=True, check=True, capture_output=True)
        main_menu()
    except (subprocess.CalledProcessError):
        print("\n============================================================")
        print(f"❌ ERRO: Não foi possível conectar à API na porta 5000.")
        print("   Por favor, inicie os serviços com o comando 'bash run.sh'")
        print("   em outro terminal antes de executar este script.")
        print("============================================================")
        sys.exit(1)
