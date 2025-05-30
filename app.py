# app.py
import sqlite3
import uuid # Para gerar IDs de sessão únicos
import json
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
# IMPORTANTE: Mude esta chave secreta para algo único e seguro!
# É usada para proteger os dados da sessão do usuário.
app.secret_key = 'x'

DATABASE = 'chatbot.db'
QUESTIONS_FILE = 'questions.json'
PROFILE_INFO = {
    "Backend": {
        "technical_name": "Desenvolvimento Backend", # Adicionando nome técnico
        "playful_track_name": "Mestre dos Códigos Ocultos",
        "playful_description": "Você tem afinidade com a construção da lógica e dos sistemas que fazem tudo funcionar 'por baixo dos panos'. É como ser o engenheiro que projeta um motor potente e confiável!",
        "superpowers": ["Lógica Afiada", "Foco em Soluções Robustas", "Visão Sistêmica"],
        "resource_suggestions": [
            "Explore linguagens como Python (com Flask/Django), Java ou Node.js.",
            "Aprenda sobre bancos de dados relacionais e NoSQL, e como construir APIs.",
            "Participe de projetos open-source focados em desenvolvimento backend."
        ],
        "advisor_summary_template": "Demonstrou forte inclinação para desenvolvimento backend, com interesse em lógica, arquitetura de sistemas e construção de funcionalidades 'server-side'."
    },
    "Frontend": {
        "technical_name": "Desenvolvimento Frontend",
        "playful_track_name": "Arquiteto(a) de Experiências Digitais",
        "playful_description": "Sua paixão é criar interfaces que as pessoas veem, usam e amam! Você se importa com a aparência, a facilidade de uso e como transformar ideias em realidade visual interativa.",
        "superpowers": ["Criatividade Visual", "Empatia com o Usuário", "Atenção aos Detalhes"],
        "resource_suggestions": [
            "Mergulhe em HTML, CSS e JavaScript (e frameworks como React, Vue ou Angular).",
            "Estude sobre design de interfaces (UI), experiência do usuário (UX) e acessibilidade web.",
            "Crie projetos pessoais para construir seu portfólio visual e interativo."
        ],
        "advisor_summary_template": "Apresentou forte interesse em desenvolvimento frontend, com foco em aspectos visuais, interatividade e experiência do usuário."
    },
    "DevOps": {
        "technical_name": "Engenharia DevOps",
        "playful_track_name": "Guardião(ã) da Eficiência Contínua",
        "playful_description": "Você gosta de garantir que tudo funcione como um relógio, automatizando processos, otimizando a infraestrutura e construindo pontes entre o desenvolvimento e as operações. É como ser o maestro de uma orquestra tecnológica!",
        "superpowers": ["Pensamento Automatizado", "Resolução Ágil de Problemas", "Colaboração Interdepartamental"],
        "resource_suggestions": [
            "Estude sobre automação de infraestrutura (ex: Terraform, Ansible), integração e entrega contínua (CI/CD com Jenkins, GitLab CI).",
            "Aprenda sobre containers (Docker, Kubernetes) e monitoramento de sistemas.",
            "Explore provedores de nuvem (AWS, Azure, GCP) e suas ferramentas de DevOps."
        ],
        "advisor_summary_template": "Mostrou afinidade com a cultura e práticas DevOps, interessando-se por automação, infraestrutura como código e eficiência de pipelines de desenvolvimento e operações."
    },
    "Cientista de Dados": {
        "technical_name": "Ciência de Dados",
        "playful_track_name": "Detetive dos Dados Secretos",
        "playful_description": "Seu superpoder é transformar números e informações em descobertas valiosas e predições! Você adora investigar, encontrar padrões, construir modelos e contar histórias com dados.",
        "superpowers": ["Curiosidade Analítica", "Raciocínio Estatístico", "Comunicação de Insights Complexos"],
        "resource_suggestions": [
            "Aprofunde-se em Python (com Pandas, NumPy, Scikit-learn, TensorFlow/PyTorch) ou R.",
            "Estude estatística, machine learning, deep learning e técnicas de visualização de dados.",
            "Participe de competições de dados (ex: Kaggle) e trabalhe em projetos com datasets reais."
        ],
        "advisor_summary_template": "Exibiu forte interesse em ciência de dados, com foco em análise exploratória, modelagem preditiva, machine learning e interpretação de grandes volumes de informação."
    },
    "Engenharia de Dados": {
        "technical_name": "Engenharia de Dados",
        "playful_track_name": "Arquiteto(a) das Grandes Hidrovias de Dados",
        "playful_description": "Você se empolga em construir e manter os 'encanamentos' e reservatórios robustos que coletam, armazenam, transformam e processam grandes volumes de dados, garantindo que eles fluam de forma confiável para onde são necessários.",
        "superpowers": ["Visão de Grande Escala", "Organização de Sistemas Complexos", "Foco em Performance e Confiabilidade"],
        "resource_suggestions": [
            "Explore tecnologias de Big Data (Spark, Hadoop), bancos de dados NoSQL e data warehouses/lakes.",
            "Aprenda sobre pipelines de dados (ETL/ELT), modelagem de dados e arquiteturas de dados distribuídas.",
            "Desenvolva projetos que envolvam a ingestão, processamento e disponibilização de grandes fluxos de informação."
        ],
        "advisor_summary_template": "Demonstrou inclinação para engenharia de dados, com interesse na construção, otimização e manutenção de sistemas e pipelines de dados em larga escala."
    },
    "Indefinido": { # Perfil de fallback
        "technical_name": "Perfil em Exploração",
        "playful_track_name": "Explorador(a) Tech em Descoberta",
        "playful_description": "Sua jornada no universo tech está apenas começando! Você demonstrou interesse em diversas áreas, o que é ótimo para quem está explorando. Continue curioso(a) para encontrar o caminho que mais te apaixona.",
        "superpowers": ["Curiosidade Aguçada", "Mente Aberta a Novidades"],
        "resource_suggestions": [
            "Participe de palestras, webinars e workshops introdutórios sobre diferentes áreas da tecnologia no IBMEC.",
            "Converse com veteranos, professores e profissionais para conhecer suas experiências.",
            "Experimente miniprojetos ou cursos online básicos em diferentes domínios para 'sentir o gostinho' de cada um."
        ],
        "advisor_summary_template": "Perfil em fase de exploração, demonstrou interesses variados ou ainda não focados. Recomenda-se mais contato com as diversas áreas tech para identificar afinidades."
    }
    # Nota: As trilhas Full-Stack e Cybersecurity não estão diretamente pontuadas
    # pelo questionário atual do Passo 4. Poderiam ser adicionadas com mais perguntas
    # ou lógicas de combinação de scores (ex: Backend + Frontend altos = Full-Stack).
}

# Carrega as perguntas do arquivo JSON
def load_questions():
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Criar um mapeamento de ID para índice para facilitar a busca da próxima pergunta
            question_list = data.get('questions', [])
            question_map = {q['id']: idx for idx, q in enumerate(question_list)}
            return data, question_list, question_map
    except FileNotFoundError:
        print(f"ERRO: Arquivo de perguntas '{QUESTIONS_FILE}' não encontrado.")
        return None, [], {}
    except json.JSONDecodeError:
        print(f"ERRO: Arquivo de perguntas '{QUESTIONS_FILE}' não é um JSON válido.")
        return None, [], {}

QUESTIONS_DATA, QUESTIONS_LIST, QUESTIONS_MAP = load_questions()
if QUESTIONS_DATA is None:
    # Se não puder carregar as perguntas, use dados de fallback ou encerre.
    # Por simplicidade, vamos permitir que a aplicação rode, mas os endpoints de API falharão.
    print("Atenção: Aplicação rodando sem dados de perguntas carregados.")


# Função para obter conexão com o banco de dados
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row # Permite acessar colunas por nome
    return db

# Função para inicializar o banco de dados (criar tabela se não existir)
def init_db():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                answer_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
        print("Banco de dados inicializado com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        if db:
            db.close()

# Rota principal para servir a interface do chat (index.html)
@app.route('/')
def index():
    # render_template busca arquivos na pasta 'templates'
    return render_template('index.html')

@app.route('/api/start_session', methods=['GET'])
def start_session():
    if not QUESTIONS_LIST: # Verifica se as perguntas foram carregadas
        return jsonify({"error": "Perguntas não carregadas no servidor."}), 500

    # Gera um ID de sessão único e o armazena na sessão do Flask
    session['session_id'] = uuid.uuid4().hex
    
    initial_question_id = QUESTIONS_DATA.get('initial_question_id')
    if not initial_question_id or initial_question_id not in QUESTIONS_MAP:
        return jsonify({"error": "ID da pergunta inicial não encontrado ou inválido."}), 500
        
    first_question = QUESTIONS_LIST[QUESTIONS_MAP[initial_question_id]]
    
    # Retorna a primeira pergunta e o ID da sessão (opcional para o cliente, mas útil para debug)
    return jsonify({
        "question": first_question,
        "session_id": session['session_id'] # Apenas para debug ou se o cliente precisar
    })

@app.route('/api/answer', methods=['POST'])
def handle_answer():
    if not QUESTIONS_LIST: # Verifica se as perguntas foram carregadas
        return jsonify({"error": "Perguntas não carregadas no servidor."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem dados JSON."}), 400

    question_id = data.get('question_id')
    # 'answer_value' pode ser o valor de uma opção de múltipla escolha ou texto livre
    answer_value = data.get('answer') 

    if not question_id or answer_value is None: # answer_value pode ser string vazia para text_input
        return jsonify({"error": "Dados incompletos: question_id e answer são obrigatórios."}), 400

    if 'session_id' not in session:
        return jsonify({"error": "Sessão não iniciada. Por favor, reinicie o chat."}), 400
    
    current_session_id = session['session_id']

    # Armazenar a resposta no banco de dados (mesma lógica do Passo 3)
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO responses (session_id, question_id, answer_text) VALUES (?, ?, ?)",
            (current_session_id, question_id, str(answer_value))
        )
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao salvar resposta no BD: {e}")
        return jsonify({"error": "Erro interno ao salvar resposta."}), 500
    finally:
        if 'db' in locals() and db:
            db.close()

    # Lógica de Ramificação para determinar a próxima pergunta
    current_question_object = None
    if question_id in QUESTIONS_MAP:
        current_question_object = QUESTIONS_LIST[QUESTIONS_MAP[question_id]]
    else:
        # Isso não deveria acontecer se o frontend envia IDs válidos
        print(f"ALERTA: ID de pergunta desconhecido recebido: {question_id}")
        return jsonify({"error": f"ID de pergunta desconhecido: {question_id}"}), 400

    next_question_id = None
    question_type = current_question_object.get('type')

    if question_type == 'multiple_choice':
        for option in current_question_object.get('options', []):
            if option['value'] == answer_value:
                next_question_id = option.get('next_question_id')
                break
        if next_question_id is None:
            print(f"ALERTA: Opção '{answer_value}' não encontrada ou sem next_question_id para pergunta '{question_id}'.")
            return jsonify({"error": "Opção de resposta inválida ou ramificação não definida para esta opção."}), 500
            
    elif question_type == 'text_input':
        next_question_id = current_question_object.get('next_question_id')
        if next_question_id is None:
            print(f"ALERTA: next_question_id não definido para pergunta text_input '{question_id}'.")
            return jsonify({"error": "Ramificação não definida para esta pergunta de texto."}), 500

    elif question_type == 'info_display':
        # Para 'info_display', a resposta do usuário (ex: "acknowledged_info") é ignorada para ramificação.
        # Apenas seguimos o 'next_question_id' definido na pergunta.
        next_question_id = current_question_object.get('next_question_id')
        if next_question_id is None:
            print(f"ALERTA: next_question_id não definido para pergunta info_display '{question_id}'.")
            return jsonify({"error": "Ramificação não definida para esta tela de informação."}), 500
    else:
        print(f"ALERTA: Tipo de pergunta desconhecido '{question_type}' para pergunta '{question_id}'.")
        return jsonify({"error": f"Tipo de pergunta desconhecido: {question_type}"}), 500

    # Processar a próxima pergunta ou finalizar
    if next_question_id == "END":
        # >>> INÍCIO DA MODIFICAÇÃO PARA O PASSO 5 <<<
        # O questionário terminou, hora de analisar o perfil!

        # 1. Buscar todas as respostas do usuário para esta sessão no banco de dados
        db_conn = None # Inicializa para garantir que existe no bloco finally
        user_responses_list = []
        try:
            db_conn = get_db()
            cursor = db_conn.cursor()
            # Ordenar por timestamp para manter a ordem das respostas, se necessário para alguma análise futura
            cursor.execute(
                "SELECT question_id, answer_text FROM responses WHERE session_id = ? ORDER BY timestamp ASC",
                (current_session_id,) # current_session_id já deve estar definido nesta função
            )
            # sqlite3.Row permite acessar colunas por nome
            user_responses_tuples = cursor.fetchall() 
            user_responses_list = [{'question_id': row['question_id'], 'answer_text': row['answer_text']} for row in user_responses_tuples]
        except sqlite3.Error as e:
            print(f"Erro ao buscar respostas do BD para análise: {e}")
            # Mesmo com erro ao buscar respostas, podemos tentar retornar uma mensagem de erro ou um perfil "Indefinido"
            # Por simplicidade, se não conseguir buscar, a análise pode resultar em "Indefinido".
        finally:
            if db_conn:
                db_conn.close()
        
        # 2. Chamar a função de análise de perfil
        # Se user_responses_list estiver vazio devido a um erro de BD, analyze_profile deve lidar com isso (ex: retornar "Indefinido")
        profile_result = analyze_profile(user_responses_list) 
        
        # 3. Armazenar o resultado da análise na sessão do Flask para ser usado pelo relatório no Passo 6
        session['profile_analysis_result'] = profile_result
        
        # 4. Retornar uma mensagem indicando que o questionário terminou e a análise está disponível
        return jsonify({
            "message": "Questionário concluído! Seus superpoderes tech estão sendo revelados...", # Mensagem atualizada
            "end_of_quiz": True,
            "profile_analysis_available": True # Novo sinalizador para o frontend
        })
        # >>> FIM DA MODIFICAÇÃO PARA O PASSO 5 <<<
    
    # Se não for "END", continua a lógica para enviar a próxima pergunta (como no Passo 4)
    elif next_question_id in QUESTIONS_MAP: # Verifique se 'elif' é necessário ou se o 'if' acima já tem return
        next_question_object = QUESTIONS_LIST[QUESTIONS_MAP[next_question_id]]
        return jsonify({"question": next_question_object})
    else:
        # Este é um erro de configuração no questions.json
        print(f"ERRO DE CONFIGURAÇÃO: next_question_id '{next_question_id}' (da pergunta '{question_id}') não é um ID de pergunta válido ou 'END'.")
        return jsonify({"error": "Erro de configuração do questionário: próxima pergunta não encontrada."}), 500

    
    if next_question_id in QUESTIONS_MAP:
        next_question_object = QUESTIONS_LIST[QUESTIONS_MAP[next_question_id]]
        return jsonify({"question": next_question_object})
    else:
        # Este é um erro de configuração no questions.json
        print(f"ERRO DE CONFIGURAÇÃO: next_question_id '{next_question_id}' (da pergunta '{question_id}') não é um ID de pergunta válido ou 'END'.")
        return jsonify({"error": "Erro de configuração do questionário: próxima pergunta não encontrada."}), 500
# Rota de teste para verificar as perguntas (mantida do Passo 1 para debug)
@app.route('/test_questions')
def test_questions_route():
    if QUESTIONS_DATA:
        return jsonify(QUESTIONS_DATA)
    return jsonify({"error": "Arquivo questions.json não carregado ou com erro."}), 500

# Adicionar em app.py

# Em app.py, dentro da função analyze_profile:

def analyze_profile(user_responses):
    scores = {
        "Backend": 0,
        "Frontend": 0,
        "DevOps": 0,
        "Cientista de Dados": 0,
        "Engenharia de Dados": 0
    }
    identified_soft_skills = set() # Usaremos um set para evitar duplicatas

    # Regras de pontuação (como no Passo 5)
    for response in user_responses:
        q_id = response['question_id']
        ans_val = response['answer_text']

        # ... (lógica de pontuação para q1_inicio até q2_dados_tipo - SEM ALTERAÇÕES AQUI) ...
        if q_id == "q1_inicio":
            if ans_val == "mundo_logico":
                scores["Backend"] += 1; scores["DevOps"] += 0.5
            elif ans_val == "mundo_visual":
                scores["Frontend"] += 1
            elif ans_val == "mundo_dados":
                scores["Cientista de Dados"] += 1; scores["Engenharia de Dados"] += 1
        elif q_id == "q2_logico_tipo":
            if ans_val == "construir_logico": scores["Backend"] += 2
            elif ans_val == "garantir_logico": scores["DevOps"] += 2
        elif q_id == "q2_visual_tipo":
            if ans_val == "bonito_facil_visual": scores["Frontend"] += 2
            elif ans_val == "info_clara_visual": scores["Cientista de Dados"] += 1; scores["Frontend"] += 0.5
        elif q_id == "q2_dados_tipo":
            if ans_val == "minerar_dados": scores["Cientista de Dados"] += 2
            elif ans_val == "construir_dados": scores["Engenharia de Dados"] += 2
        
        # >>> INÍCIO DAS NOVAS LÓGICAS DE PONTUAÇÃO/ANÁLISE <<<
        elif q_id == "q_ambiente_pref":
            # Esta pergunta pode não pontuar diretamente para uma trilha tech,
            # mas pode influenciar a descrição ou sugestões, ou ser um "superpoder".
            if ans_val == "colaborativo_intenso":
                identified_soft_skills.add("Trabalho em Equipe Intenso")
            elif ans_val == "foco_individual":
                identified_soft_skills.add("Foco e Concentração Profunda")
            elif ans_val == "equilibrio_times":
                identified_soft_skills.add("Equilíbrio entre Colaboração e Foco")
            # Exemplo: Poderia dar um leve direcionamento se combinado com outras respostas
            # if ans_val == "foco_individual" and scores["Backend"] > 0 : scores["Backend"] += 0.2

        elif q_id == "q_soft_resolucao_grupo":
            if ans_val == "brainstorm_equipe_soft":
                identified_soft_skills.add("Colaboração Efetiva")
                identified_soft_skills.add("Comunicação Proativa")
            elif ans_val == "pesquisa_solitaria_soft":
                identified_soft_skills.add("Autonomia na Resolução")
                identified_soft_skills.add("Persistência")
            elif ans_val == "abordagem_diferente_soft":
                identified_soft_skills.add("Pensamento Crítico Aplicado")
                identified_soft_skills.add("Comunicação Clara")
        # >>> FIM DAS NOVAS LÓGICAS <<<

    # ... (lógica para determinar primary_track_name e obter track_details - SEM ALTERAÇÕES AQUI) ...
    primary_track_name = "Indefinido"; highest_score = 0
    if any(s > 0 for s in scores.values()):
        primary_track_name = max(scores, key=scores.get)
        highest_score = scores[primary_track_name]
        if highest_score == 0: primary_track_name = "Indefinido"
    track_details = PROFILE_INFO.get(primary_track_name, PROFILE_INFO["Indefinido"])
    
    # Atualizar a forma como os "superpoderes" são definidos:
    # Se identificamos soft skills, usamos elas. Senão, usamos os genéricos da trilha.
    final_superpowers = list(identified_soft_skills) if identified_soft_skills else track_details["superpowers"]
    if not identified_soft_skills and primary_track_name == "Indefinido": # Caso especial para Indefinido sem soft skill
        final_superpowers = PROFILE_INFO["Indefinido"]["superpowers"]


    advisor_summary = track_details["advisor_summary_template"]
    formatted_scores = ", ".join([f"{track}: {score}" for track, score in scores.items()])
    advisor_summary += f" (Contexto de pontuação: {formatted_scores})."
    if identified_soft_skills:
         advisor_summary += f" Soft skills indicadas: {', '.join(list(identified_soft_skills))}."


    profile_data = {
        "technical_track": track_details["technical_name"],
        "playful_track_name": track_details["playful_track_name"],
        "playful_description": track_details["playful_description"],
        "superpowers": final_superpowers, # <-- ATUALIZADO AQUI
        "resource_suggestions": track_details["resource_suggestions"],
        "advisor_summary": advisor_summary, # <-- Resumo do advisor agora pode incluir soft skills
        "raw_answers": user_responses
    }
    return profile_data
@app.route('/report')
def report():
    # Recupera os dados da análise da sessão
    profile_data = session.get('profile_analysis_result')

    if not profile_data:
        # Se não houver dados na sessão, redireciona para o início ou mostra um erro
        # Idealmente, o usuário só chega aqui se profile_analysis_available foi True
        return "Resultado da análise não encontrado. Por favor, complete o questionário primeiro. <a href='/'>Voltar ao início</a>"

    # Opcional, mas recomendado: Enriquecer as respostas brutas com o texto da pergunta
    # para o relatório do consultor ser mais claro.
    # Isso requer acesso a QUESTIONS_LIST e QUESTIONS_MAP.
    augmented_raw_answers = []
    if QUESTIONS_LIST and QUESTIONS_MAP: # Verifica se as perguntas foram carregadas
        for ans in profile_data.get('raw_answers', []):
            question_text = "Texto da pergunta não encontrado (ID: " + ans.get('question_id', 'N/A') + ")"
            if ans.get('question_id') in QUESTIONS_MAP:
                try:
                    question_text = QUESTIONS_LIST[QUESTIONS_MAP[ans['question_id']]]['text']
                except (KeyError, IndexError) as e:
                    print(f"Erro ao buscar texto da pergunta para ID {ans.get('question_id')}: {e}")
            
            augmented_raw_answers.append({
                'question_text': question_text,
                'answer_text': ans.get('answer_text', 'N/A')
            })
        # Substitui as respostas brutas no profile_data pelos dados enriquecidos
        profile_data['augmented_raw_answers'] = augmented_raw_answers
    else:
        # Se as perguntas não puderam ser carregadas, as respostas brutas não serão aumentadas
        # mas o relatório ainda pode ser gerado com os IDs das perguntas.
        profile_data['augmented_raw_answers'] = profile_data.get('raw_answers', [])


    # Renderiza o template report.html, passando os dados do perfil
    return render_template('report.html', profile=profile_data)

if __name__ == '__main__':
    init_db() # Inicializa o banco de dados na inicialização da aplicação
    app.run(debug=True, port=5000) # Especificar a porta é uma boa prática