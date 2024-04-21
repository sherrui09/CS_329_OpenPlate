document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('sendButton');
    const inputBox = document.getElementById('userInput');
    const chatBox = document.getElementById('chatbox');
    const apiKeyModal = document.getElementById('apiKeyModal');
    const welcomeModal = document.getElementById('welcomeModal');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const apiKeySubmit = document.getElementById('apiKeySubmit');
    const apiButton = document.getElementById('apiButton');
    const closeButtons = document.querySelectorAll('.close');

    // Show the welcome modal on load
    welcomeModal.style.display = "block";

    // Event listeners for closing modals
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            closeModal(button.closest('.modal').id);
        });
    });

    // Open API key modal when the API key button is clicked
    apiButton.addEventListener('click', function() {
        apiKeyModal.style.display = "block";
    });

    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target.className === 'modal') {
            closeModal(event.target.id);
        }
    };

    apiKeySubmit.addEventListener('click', function() {
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            alert("Please enter an API Key.");
            return;
        }
        localStorage.setItem('apiKey', apiKey);  // Store API key in localStorage
        fetch('/set_api_key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({apiKey: apiKey})
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);  // Show success message
                apiKeyModal.style.display = "none";
                apiButton.classList.remove('pulse');
            } else {
                alert(data.error);  // Show error message
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Failed to set API key due to an error.");
        });
    });

    sendButton.addEventListener('click', sendMessage);
    inputBox.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
            event.preventDefault();  // Prevent form submit on enter press
        }
    });

    function sendMessage() {
        const userMessage = inputBox.value.trim();
        const apiKey = localStorage.getItem('apiKey');
        if (!userMessage) {
            alert("Please type a message.");
            return;
        }

        chatBox.value += "You: " + userMessage + "\n";
        inputBox.value = "";  // Clear input box

        if (!apiKey) {
            chatBox.value += "Assistant: Please enter an API key to proceed.\n";
            apiKeyModal.style.display = "block";
            apiButton.classList.add('pulse');
            return;
        }

        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({message: userMessage}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.type === "chat") {
                chatBox.value += "Assistant: " + data.message + "\n";
            } else if (data.type === "popup") {
                displayPopup(data.message);
            } else if (data.type === "both") {
                // need to check which popup it's for
                chatBox.value += "Assistant: " + data.chat_message + "\n";
                displayPopup(data.popup_message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            chatBox.value += "Assistant: I encountered an error. Please try again.\n";
        });
    }

    function displayPopup(message) {
        const notificationModal = document.getElementById('notificationModal');
        document.getElementById('modalMessage').textContent = message;
        notificationModal.style.display = 'block';
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }
});
