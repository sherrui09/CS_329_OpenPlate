document.addEventListener('DOMContentLoaded', function() {
    console.log("IM IN")
    const sendButton = document.getElementById('sendButton');
    const inputBox = document.getElementById('userInput');
    const chatBox = document.getElementById('botbox'); // This is going to display Our Model's OUTPUT
    const userBox = document.getElementById('userbox'); // This is going to display Our User's  INPUT
    const apiKeyModal = document.getElementById('apiKeyModal');
    const welcomeModal = document.getElementById('welcomeModal');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const apiKeySubmit = document.getElementById('apiKeySubmit');
    const apiButton = document.getElementById('apiButton');
    const userProfile = document.getElementById('userProfile')
    if (userProfile) {
        userProfile.addEventListener("click", showUserProfile);
    }

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
        // Disable input box
        inputBox.disabled = true;

        const userMessage = inputBox.value.trim();
        console.log(userMessage)
        const apiKey = localStorage.getItem('apiKey');
        if (!userMessage) {
            alert("Please type a message.");
            // Enable input box
            inputBox.disabled = false;
            return;
        }

        let riceBowlSpan = document.createElement('span'); // make a ricebowl icon for the BOT
        let userIconSpan = document.createElement('span')  // make a user icon for USER
        riceBowlSpan.className = 'material-symbols-outlined';
        userIconSpan.className = 'material-symbols-outlined';
        riceBowlSpan.textContent = 'rice_bowl';
        userIconSpan.textContent = 'person';


        // REASON FOR HTML IN JS FILE ---> Need to dynamically update chat. Cannot dynamically update in HTML (to my limited knowledge)
        let userBoxDiv = document.createElement('div')   // make new div
        userBoxDiv.className = 'user-message';
        userBoxDiv.textContent = `${userMessage}`; // Use <br> for newline

        const userBoxLi = document.createElement('li');
        userBoxLi.className = 'chat incoming';
        userBoxLi.appendChild(userIconSpan); // for user icon
        userBoxLi.appendChild(userBoxDiv);
        

        let chatBox = document.querySelector('.chatbox') // make a NEW chatbox obj for DISPLAY
        chatBox.appendChild(userBoxLi)
        
        chatBox.scrollTop = chatBox.scrollHeight;

        // chatBox.value += "You: " + userMessage + "\n";
        // userBox.value += "You: " + userMessage + "\n";

        inputBox.value = "";  // Clear input box
        if (!apiKey) {
            chatBox.value += "Assistant: Please enter an API key to proceed.\n";
            apiKeyModal.style.display = "block";
            apiButton.classList.add('pulse');
            // Enable input box
            inputBox.disabled = false;
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
            let botBoxDiv = document.createElement('div')   // make new div
            botBoxDiv.className = 'bot-message';
            botBoxDiv.textContent = `\n${data.message}`;
            console.log(data.message)

            const botBoxLi = document.createElement('li');
            botBoxLi.className = 'chat incoming';
            botBoxLi.appendChild(riceBowlSpan); // this is where ricebowl comes in
            botBoxLi.appendChild(botBoxDiv);
            
            if (data.type === "chat") {
                let chatBox = document.querySelector('.chatbox') // make a NEW chatbox obj for DISPLAY
                chatBox.appendChild(botBoxLi)
                chatBox.scrollTop = chatBox.scrollHeight;

                // chatBox.innerHTML += "Assistant: " + data.message + "\n";
                // chatBox.value += "Assistant: " + data.message + "\n";

            } else if (data.type === "popup") {
                displayPopup(data.message);
            } else if (data.type === "both") {
                
                let chatBox = document.querySelector('.chatbox') // make a NEW chatbox obj for DISPLAY
                chatBox.appendChild(botBoxLi)
                chatBox.scrollTop = chatBox.scrollHeight;

                // chatBox.innerHTML += "Assistant: " + data.chat_message + "\n";
                // chatBox.value += "Assistant: " + data.chat_message + "\n";

                displayPopup(data.popup_message);
            }

            // Enable input box
            inputBox.disabled = false;
        })
        .catch((error) => {
            console.error('Error:', error);
            let botBoxDiv = document.createElement('div')   // make new div
            botBoxDiv.className = 'bot-message';
            botBoxDiv.textContent = "Assistant\n: I encountered an error. Please try again.\n";
            let chatBox = document.querySelector('.chatbox') // make a NEW chatbox obj for DISPLAY
            chatBox.appendChild(botBoxDiv)
            chatBox.scrollTop = chatBox.scrollHeight;

            // chatBox.innerHTML += "Assistant: I encountered an error. Please try again.\n";
            // chatBox.value += "Assistant: I encountered an error. Please try again.\n";

            // Enable input box
            inputBox.disabled = false;
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


    function showUserProfile() {
        const userProfileModal = document.getElementById('userProfileModal');
        fetch('/user_profile', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(response => response.json())
        .then(data => {
            // Populate modal with user profile data
            const userProfileContent = document.getElementById('userProfileContent');
            userProfileContent.innerHTML = ''; // Clear previous content
            for (const [key, value] of Object.entries(data)) {
                const row = document.createElement('div');
                row.classList.add('row');
                const keyElement = document.createElement('div');
                keyElement.classList.add('key');
                keyElement.textContent = key.charAt(0).toUpperCase() + key.slice(1) + ':';
                const valueElement = document.createElement('div');
                valueElement.classList.add('value');
                valueElement.textContent = value !== null ? value : 'Not provided';
                row.appendChild(keyElement);
                row.appendChild(valueElement);
                userProfileContent.appendChild(keyElement);
                userProfileContent.appendChild(valueElement);
            }
            // Show user profile modal
            userProfileModal.style.display = 'block';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
});
