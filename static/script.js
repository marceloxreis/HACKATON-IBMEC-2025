// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const inputControls = document.getElementById('inputControls'); // Área para inputs dinâmicos
    let currentQuestion = null; // Para armazenar os dados da pergunta atual

    // Função para adicionar uma mensagem à interface do chat
    function addMessage(messageText, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender === 'bot' ? 'bot-message' : 'user-message');
        
        const paragraphElement = document.createElement('p');
        paragraphElement.innerHTML = messageText; // Usar innerHTML para renderizar <br> se necessário
        messageElement.appendChild(paragraphElement);
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Função para renderizar os controles de input (texto ou botões)
    function renderInputControls(question) {
        inputControls.innerHTML = ''; // Limpa controles anteriores
        currentQuestion = question; // Atualiza a pergunta atual globalmente no JS

        if (question.type === 'text_input') {
            const inputField = document.createElement('input');
            inputField.type = 'text';
            inputField.id = 'userInput';
            inputField.placeholder = 'Digite sua resposta aqui...';
            
            const sendButton = document.createElement('button');
            sendButton.id = 'sendButton';
            sendButton.textContent = 'Enviar';
            
            sendButton.addEventListener('click', handleSendTextMessage);
            inputField.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    handleSendTextMessage();
                }
            });

            inputControls.appendChild(inputField);
            inputControls.appendChild(sendButton);
            inputField.focus();
        } else if (question.type === 'multiple_choice' && question.options) {
            question.options.forEach(option => {
                const optionButton = document.createElement('button');
                optionButton.classList.add('option-button');
                optionButton.textContent = option.text;
                optionButton.dataset.value = option.value;
                
                optionButton.addEventListener('click', () => {
                    // Passa o texto da opção para exibição e o valor para o backend
                    handleSendChoiceMessage(option.text, option.value); 
                });
                inputControls.appendChild(optionButton);
            });
        } else if (question.type === 'info_display') { // NOVO CASO AQUI
            const continueButton = document.createElement('button');
            continueButton.classList.add('option-button'); // Reutilizando estilo
            continueButton.textContent = "Continuar";
            
            continueButton.addEventListener('click', () => {
                // Para info_display, a "resposta" é apenas um reconhecimento para avançar.
                // Exibimos uma mensagem de "Ok" do usuário para manter o fluxo visual do chat.
                addMessage("Ok", 'user'); 
                // Enviamos um valor convencional, já que o backend ignora o conteúdo da resposta para info_display.
                sendAnswerToBackend(currentQuestion.id, "acknowledged_info"); 
            });
            inputControls.appendChild(continueButton);
        }
    }
    
    // Função para lidar com o envio de resposta de texto
    function handleSendTextMessage() {
        const userInputField = document.getElementById('userInput');
        if (!userInputField) return;

        const text = userInputField.value.trim();
        if (text !== '' && currentQuestion) {
            addMessage(text, 'user');
            sendAnswerToBackend(currentQuestion.id, text);
            userInputField.value = '';
        }
    }

    // Função para lidar com o envio de resposta de múltipla escolha
    function handleSendChoiceMessage(displayText, valueToSend) {
        if (currentQuestion) {
            addMessage(displayText, 'user'); // Mostra o texto da opção escolhida
            sendAnswerToBackend(currentQuestion.id, valueToSend); // Envia o valor da opção
        }
    }

    // Função para enviar a resposta para o backend
    async function sendAnswerToBackend(questionId, answer) {
        try {
            const response = await fetch('/api/answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: questionId,
                    answer: answer,
                }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Erro HTTP: ${response.status}`);
            }
            const data = await response.json();
            handleBackendResponse(data);
        } catch (error) {
            console.error('Erro ao enviar resposta:', error);
            addMessage(`Erro ao me comunicar com o servidor: ${error.message}. Tente novamente mais tarde.`, 'bot');
        }
    }

    // Função para processar a resposta do backend (próxima pergunta ou fim)
    function handleBackendResponse(data) {
        if (data.end_of_quiz && data.profile_analysis_available) { // MODIFICADO AQUI
            addMessage(data.message, 'bot'); // Ex: "Questionário concluído! Seus superpoderes tech estão sendo revelados..."
            inputControls.innerHTML = '<p style="text-align:center; padding:10px;">Preparando seu relatório personalizado...</p>';
            
            // Redireciona para a página de relatório após um pequeno atraso
            setTimeout(() => {
                window.location.href = '/report'; // Redireciona o navegador para a rota /report
            }, 2500); // Atraso de 2.5 segundos para o usuário ler a mensagem final

        } else if (data.question) {
            currentQuestion = data.question;
            const formattedQuestionText = currentQuestion.text.replace(/\n/g, '<br>');
            addMessage(formattedQuestionText, 'bot');
            renderInputControls(currentQuestion);
        } else if (data.error) {
            addMessage(`Erro do servidor: ${data.error}`, 'bot');
            inputControls.innerHTML = '';
        }
    }

    // Função para iniciar a sessão e buscar a primeira pergunta
    async function startChat() {
        try {
            const response = await fetch('/api/start_session');
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Erro HTTP: ${response.status}`);
            }
            const data = await response.json();
            handleBackendResponse(data); // Processa a primeira pergunta
        } catch (error) {
            console.error('Erro ao iniciar chat:', error);
            addMessage(`Não consegui iniciar nossa conversa: ${error.message}. Verifique o console ou tente recarregar.`, 'bot');
        }
    }

    // Inicia o chat quando a página carrega
    startChat();
});