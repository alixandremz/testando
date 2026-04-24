print("Dev de usuários")
def cadastrar_usuario():
    nome = input('Nome: ')
    email = input('Email: ')
    senha = input('Senha: ')
    tipo = input('Tipo (morador/servidor): ')

    try:
        arquivo = open('usuarios.txt', 'r')
        linhas = arquivo.readlines()
        arquivo.close()
        novo_id = len(linhas) + 1
    except:
        novo_id = 1

    arquivo = open('usuarios.txt', 'a')
    linha = str(novo_id) + ',' + nome + ',' + email + ',' + senha + ',' + tipo + '\n'
    arquivo.write(linha)
    arquivo.close()

    print('Usuário cadastrado!')


def login():
    email = input('Email: ')
    senha = input("Senha: ")

    arquivo = open('usuarios.txt', 'r')
    
    for linha in arquivo:
        dados = linha.strip().split(',')

        if dados[2] == email and dados[3] == senha:
            print('Login feito!')
            print('Bem-vindo', dados[1])
            arquivo.close()
            return

    arquivo.close()
    print('Erro no login!')


def listar():
    arquivo = open('usuarios.txt', 'r')

    for linha in arquivo:
        print(linha.strip())

    arquivo.close()


while True:
    print('\n1 - Cadastrar')
    print('2 - Login')
    print('3 - Listar')
    print('4 - Sair')

    opcao = input('Escolha: ')

    if opcao == '1':
        cadastrar_usuario()
    elif opcao == '2':
        login()
    elif opcao == '3':
        listar()
    elif opcao == '4':
        break
    else:
        print('Opção inválida')
