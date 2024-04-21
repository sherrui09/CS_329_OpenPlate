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
            button.closest('.modal').style.display = "none";
        });
    });

    // Open API key modal when the API key button is clicked
    apiButton.addEventListener('click', function() {
        apiKeyModal.style.display = "block";
    });

    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target.className === 'modal') {
            event.target.style.display = "none";
        }
    }
    
    apiKeySubmit.addEventListener('click', function() {
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            alert("Please enter an API Key.");
            return;
        }
        fetch('/set_api_key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({apiKey: apiKey})
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);  // Success
                apiKeyModal.style.display = "none";
                apiButton.classList.remove('pulse');  // Stop pulsating the button
            } else {
                alert(data.error);  // Error handling
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Failed to set API key due to an error.");
        });
    });
    

    

    // Sending a message
    sendButton.addEventListener('click', sendMessage);
    inputBox.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
            event.preventDefault(); // Prevent form submit on enter press
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
        inputBox.value = ""; // clear input box

        if (!apiKey) {
            chatBox.value += "Assistant: Please enter an API key to proceed.\n";
            apiKeyModal.style.display = "block";
            apiButton.classList.add('pulse'); // Start pulsating the button
            return;
        }

        // Simulate API call
        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({message: userMessage}),
        })
        .then(response => response.text()) // Parse response as text
        .then(body => {
            chatBox.value += "Assistant: " + body + "\n"; // Add the response to the chat box
        })
        .catch((error) => {
            console.error('Error:', error);
            chatBox.value += "Assistant: I encountered an error. Please try again.\n";
        });
    }
});
