document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chatBox');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatSubmit = document.getElementById('chatSubmit');
    const chatLoading = document.getElementById('chatLoading');
    const clearChatBtn = document.getElementById('clearChat');

    // Auto-scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    // Chat form submission with AJAX
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const userInput = chatInput.value.trim();
        if (!userInput) return;

        chatLoading.style.display = 'block';
        chatSubmit.disabled = true;

        const userDiv = document.createElement('div');
        userDiv.className = 'chat-message user-message';
        userDiv.style.opacity = '0';
        userDiv.textContent = userInput;
        chatBox.appendChild(userDiv);
        setTimeout(() => userDiv.style.opacity = '1', 10);

        $.ajax({
            url: '/chat',
            method: 'POST',
            data: { chat_input: userInput },
            success: function(response) {
                const botDiv = document.createElement('div');
                botDiv.className = 'chat-message bot-message';
                botDiv.style.opacity = '0';
                botDiv.textContent = response.bot;
                chatBox.appendChild(botDiv);
                setTimeout(() => botDiv.style.opacity = '1', 10);
                chatBox.scrollTop = chatBox.scrollHeight;
                chatInput.value = '';
            },
            error: function() {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'chat-message bot-message';
                errorDiv.style.color = '#d9534f';
                errorDiv.textContent = 'Error occurred. Try again!';
                chatBox.appendChild(errorDiv);
            },
            complete: function() {
                chatLoading.style.display = 'none';
                chatSubmit.disabled = false;
            }
        });
    });

    // Clear chat
    clearChatBtn.addEventListener('click', function() {
        $.ajax({
            url: '/clear_chat',
            method: 'POST',
            success: function() {
                chatBox.innerHTML = '<div class="chat-message bot-message">Which language would you like? English, Hindi, tamil?</div>';
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        });
    });
});