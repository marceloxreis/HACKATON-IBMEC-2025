# MentorIA Carreiras IBMEC - MVP

## Descrição do Projeto

O "MentorIA Carreiras IBMEC" é um aplicativo web desenvolvido como um Produto Mínimo Viável (MVP). Seu objetivo principal é auxiliar alunos dos primeiros períodos dos cursos de Engenharia de Software, Engenharia de Computação e Ciência de Dados do IBMEC a explorarem afinidades com diferentes carreiras na área de tecnologia. Através de um chatbot lúdico e interativo, a aplicação mapeia o perfil do aluno, sugere trilhas de carreira compatíveis e fornece relatórios personalizados para o aluno e para a equipe de Carreiras do IBMEC.

## Índice (Opcional, mas recomendado para READMEs longos)

* [Funcionalidades do MVP](#funcionalidades-do-mvp)
* [Tecnologias Utilizadas](#tecnologias-utilizadas)
* [Estrutura do Projeto](#estrutura-do-projeto)
* [Pré-requisitos](#pré-requisitos)
* [Configuração e Instalação Local](#configuração-e-instalação-local)
* [Executando a Aplicação](#executando-a-aplicação)
* [Como Usar a Aplicação](#como-usar-a-aplicação)
* [Entendendo e Modificando o Questionário](#entendendo-e-modificando-o-questionário)
* [Principais Arquivos do Projeto](#principais-arquivos-do-projeto)
* [Contribuição](#contribuição)
* [Próximos Passos / Melhorias Futuras](#próximos-passos--melhorias-futuras)
* [License](#license)

## Funcionalidades do MVP

* **Chatbot Interativo:** Interface de chat com perguntas e opções de múltipla escolha ou entrada de texto.
* **Lógica de Ramificação:** O fluxo de perguntas se adapta com base nas respostas do aluno.
* **Armazenamento de Respostas:** As respostas são salvas em um banco de dados SQLite.
* **Análise de Perfil Simplificada:** Um conjunto de regras no backend analisa as respostas para classificar o aluno em uma trilha tech.
* **Relatórios Personalizados:**
    * **Relatório do Aluno ("Seu Superpoder Tech"):** Apresentação lúdica da trilha, superpoderes e sugestões.
    * **Relatório do Consultor ("Raio-X Tech do Aluno"):** Resumo técnico, justificativa e respostas brutas do aluno.
* **"Salvar como PDF":** Os relatórios são páginas web que podem ser facilmente salvas como PDF através da funcionalidade do navegador.

## Tecnologias Utilizadas

* **Backend:** Python 3.x com Micro-framework Flask
* **Banco de Dados:** SQLite 3
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla/Puro)
* **Gerenciamento de Sessão:** Flask Sessions
* **Formato de Dados para Perguntas:** JSON
* **Controle de Versão:** Git e GitHub

## Pré-requisitos

* Python 3.7 ou superior
* `pip` (gerenciador de pacotes Python)
* Git (para clonar o repositório)

## Configuração e Instalação Local

1.  **Clone o Repositório:**
    Abra seu terminal e clone este repositório para sua máquina local:
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO_NO_GITHUB>
    ```
    Substitua `<URL_DO_SEU_REPOSITORIO_NO_GITHUB>` pela URL real do seu projeto no GitHub.

2.  **Navegue até a Pasta do Projeto:**
    ```bash
    cd tech-path-finder-ibmec
    ```

3.  **Crie um Ambiente Virtual:**
    É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.
    ```bash
    python -m venv venv
    ```

4.  **Ative o Ambiente Virtual:**
    * No Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    * No macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    Você verá `(venv)` no início do seu prompt do terminal.

5.  **Instale as Dependências:**
    Com o ambiente virtual ativo, instale as bibliotecas Python necessárias:
    ```bash
    pip install -r requirements.txt
    ```

6.  **Configure a Chave Secreta do Flask:**
    * Abra o arquivo `app.py`.
    * Encontre a linha: `app.secret_key = 'coloque-uma-chave-secreta-muito-segura-aqui!'`
    * **IMPORTANTE:** Altere o valor `'coloque-uma-chave-secreta-muito-segura-aqui!'` para uma string longa, aleatória e segura. Esta chave é usada para proteger os dados da sessão.
    * **Segurança:** Para projetos reais compartilhados ou em produção, esta chave não deve ser versionada diretamente no código. Considere o uso de variáveis de ambiente.

7.  **Banco de Dados e `.gitignore`:**
    * O banco de dados SQLite (`chatbot.db`) será criado automaticamente na primeira vez que você executar a aplicação, devido à função `init_db()` em `app.py`.
    * **Recomendação para `.gitignore`:** Crie um arquivo chamado `.gitignore` na raiz do seu projeto para evitar que arquivos desnecessários ou sensíveis sejam enviados para o GitHub. Sugestões para o `.gitignore`:
      ```
      # Ambiente Virtual
      venv/
      */venv/
      .*/venv/

      # Arquivos Python compilados e caches
      __pycache__/
      *.py[cod]
      *$py.class

      # Arquivos de Banco de Dados (se não quiser versionar os dados locais)
      *.db
      *.sqlite
      *.sqlite3

      # Arquivos de IDE e Sistema Operacional
      .vscode/
      .idea/
      .DS_Store
      Thumbs.db

      # Arquivos de configuração local (se houver)
      .env
      ```
    * **Nota sobre `chatbot.db`:** Se você adicionar `*.db` ao `.gitignore`, cada desenvolvedor terá seu próprio banco de dados local. Se você precisar de um banco de dados com dados iniciais para todos, considere uma estratégia de "seed" ou um script de inicialização mais elaborado.

## Executando a Aplicação

1.  Certifique-se de que seu ambiente virtual (`venv`) está ativo.
2.  Navegue até a pasta raiz do projeto no terminal.
3.  Execute o comando:
    ```bash
    python app.py
    ```
4.  Você deverá ver mensagens indicando que o servidor Flask está rodando, geralmente em `http://127.0.0.1:5000/`.

## Como Usar a Aplicação

1.  Abra seu navegador web.
2.  Acesse o endereço `http://127.0.0.1:5000/`.
3.  Interaja com o chatbot respondendo às perguntas.
4.  Ao final do questionário, você será redirecionado para a página de relatório. O relatório pode ser salvo em PDF usando a funcionalidade "Imprimir" do seu navegador e escolhendo "Salvar como PDF".

## Entendendo e Modificando o Questionário

A lógica central do chatbot reside em dois lugares principais:

* **`questions.json`:**
    * Este arquivo define todas as perguntas, seus tipos (`multiple_choice`, `text_input`, `info_display`), as opções de resposta (com `value`, `text` e `next_question_id`) e o fluxo de ramificação através dos campos `next_question_id`.
    * Para adicionar ou modificar perguntas, edite este arquivo cuidadosamente, garantindo IDs únicos e que todos os caminhos levem a uma pergunta válida ou ao marcador `"END"`.

* **`app.py` (Função `analyze_profile` e Dicionário `PROFILE_INFO`):**
    * A função `analyze_profile` contém a lógica de pontuação que interpreta as respostas do usuário (com base nos `question_id` e nos `value` das respostas) para determinar a trilha tech e identificar soft skills.
    * O dicionário `PROFILE_INFO` contém os textos descritivos, nomes lúdicos, superpoderes e sugestões para cada trilha.
    * Ao adicionar novas perguntas que devem influenciar o perfil, a função `analyze_profile` precisará ser atualizada para incorporar essa nova lógica.

## Principais Arquivos do Projeto

* **`app.py`**: Contém toda a lógica do servidor backend Flask.
* **`questions.json`**: Define a estrutura e o conteúdo do questionário.
* **`static/script.js`**: Controla a interatividade do frontend e a comunicação com a API.
* **`static/style.css`**: Estilização visual.
* **`templates/index.html`**: Estrutura HTML da interface do chat.
* **`templates/report.html`**: Estrutura HTML da página de relatório.
* **`requirements.txt`**: Lista de dependências Python.
* **`README.md`**: Este arquivo de documentação.
* **`.gitignore`**: Especifica arquivos não rastreados pelo Git.
