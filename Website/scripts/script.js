document.addEventListener("DOMContentLoaded", function() {
const chatbox = document.querySelector(".chatbox"); // from index.html
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
let userMessage = null; // Variable to store user's message
const inputInitHeight = chatInput.scrollHeight;

console.log(chatInput)

function handleChat() {
    userMessage = chatInput.value.trim();
    console.log(userMessage)

    fetch('http://127.0.0.1:5000', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userMessage }) // what is being sent.
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // fetch('/', {
    //     method: 'POST', // post to send data
    //     headers: {
    //         'Content-Type': 'application/json'
    //     },
    //     body: JSON.stringify({ message: message })
    // })
    // .then(response => response.json())
    // .then(data => {
    //     // Handle the response from the server
    //     displayMessage(data.response, 'incoming');
    // });
}

function displayMessage(message, className) {
    const chatLi = createChatLi(message, className);
    // Append the chat message to the chat interface
    document.getElementById('chat').appendChild(chatLi);
}





    // const createChatLi = (message, className) => {
    //     // Create a chat <li> element with passed message and className
    //     const chatLi = document.createElement("li");
    //     chatLi.classList.add("chat", `${className}`);
    //     let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">rice_bowl</span><p></p>`;
    //     chatLi.innerHTML = chatContent;
    //     chatLi.querySelector("p").textContent = message;
    //     return chatLi; // return chat <li> element
    // }

    // const generateResponse = (chatElement) => {
    //     const API_URL = "https://api.openai.com/v1/chat/completions";
    //     console.log(chatElement)
    //     // INSERT API KEY HERE
    //     const API_KEY = 'sk-proj-gIVT0BckeOFsyxCGajEHT3BlbkFJdV0vjiszJJcIOCSOVmWw' 

    //     const messageElement = chatElement.querySelector("p");

    //     // Define the properties and message for the API request
    //     const requestOptions = {
    //         method: "POST",
    //         headers: {
    //             "Content-Type": "application/json",
    //             "Authorization": `Bearer ${API_KEY}` // Remember to replace API_KEY with your actual API key
    //         },
    //         body: JSON.stringify({
    //             model: "gpt-3.5-turbo",
    //             messages: [{role: "user", content: userMessage}],
    //         })
    //     }

    //     // Send POST request to API, get response and set the reponse as paragraph text
    //     fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
    //         messageElement.textContent = data.choices[0].message.content.trim();
    //     }).catch(() => {
    //         messageElement.classList.add("error");
    //         messageElement.textContent = "Oops! Something went wrong. Please try again.";
    //     }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
    // }

    // const handleChat = () => {
    //     userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
    //     if(!userMessage) return;
    //     console.log(userMessage)
    //     // Clear the input textarea and set its height to default
    //     chatInput.value = "";
    //     chatInput.style.height = `${inputInitHeight}px`;

    //     // Append the user's message to the chatbox
    //     chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    //     chatbox.scrollTo(0, chatbox.scrollHeight);
        
    //     setTimeout(() => {
    //         // Display "Thinking..." message while waiting for the response
    //         const incomingChatLi = createChatLi("Thinking...", "incoming");
    //         console.log(incomingChatLi);
    //         chatbox.appendChild(incomingChatLi);
    //         chatbox.scrollTo(0, chatbox.scrollHeight);
    //         generateResponse(incomingChatLi);
    //     }, 600);
    // }

    chatInput.addEventListener("input", () => {
        // Adjust the height of the input textarea based on its content
        chatInput.style.height = `${inputInitHeight}px`;
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    chatInput.addEventListener("keydown", (e) => {
        // If Enter key is pressed without Shift key and the window 
        // width is greater than 800px, handle the chat
        if(e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleChat();
        }
    });
sendChatBtn.addEventListener("click", handleChat); })
