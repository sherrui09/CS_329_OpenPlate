document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('sendButton');
    const inputBox = document.getElementById('userInput');
    const chatBox = document.getElementById('chatbox');

    sendButton.addEventListener('click', sendMessage);
    inputBox.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const userMessage = inputBox.value.trim();

        if (!userMessage) {
            alert("Please type a message.");
            return;
        }

        chatBox.value += "You: " + userMessage + "\n";
        inputBox.value = "";  // clear input box

        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({message: userMessage}),
        })
        .then(response => {
            console.log('Response:', response);
            return response.text(); // Parse response as text
        })
        .then(body => {
            console.log('Response Body:', body); // Log the response body
            chatBox.value += "Assistant: " + body + "\n"; // Add the response to the chat box
        })
        .catch((error) => {
            console.error('Error:', error);
            chatBox.value += "Assistant: I encountered an error. Please try again.\n";
        });
        
        
    }
});
