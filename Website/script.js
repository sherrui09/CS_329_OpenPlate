document.addEventListener("DOMContentLoaded", function() {
    
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    let userMessage = null; // Variable to store user's message
    const inputInitHeight = chatInput.scrollHeight;

    const createChatLi = (message, className) => {
        // Create a chat <li> element with passed message and className
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", `${className}`);
        let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">rice_bowl</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi; // return chat <li> element
    }

    const generateResponse = (chatElement) => {
        const API_URL = "https://api.openai.com/v1/chat/completions";

        // INSERT API KEY HERE
        const API_KEY = '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' 

        const messageElement = chatElement.querySelector("p");

        // Define the properties and message for the API request
        const requestOptions = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${API_KEY}` // Remember to replace API_KEY with your actual API key
            },
            body: JSON.stringify({
                model: "gpt-3.5-turbo",
                messages: [
                    { role: "system", content: "You are an intelligent meal planner assistant. Your primary task is to gather information about the user (including weight, height, goal) and to understand user queries related to meal planning and provide helpful responses. This includes recognizing the user's intent (e.g., seeking a recipe, needing a shopping list, asking for nutritional advice) and identifying specific details (slots) such as dietary preferences, meal types, preferred cuisines, and ingredients. You should also consider users' dietary restrictions and nutritional goals when providing recommendations." },
                    {role: "user", content: userMessage}
                ],
            })
        }

        // Send POST request to API, get response and set the reponse as paragraph text
        fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
            messageElement.textContent = data.choices[0].message.content.trim();
        }).catch(() => {
            messageElement.classList.add("error");
            messageElement.textContent = "Oops! Something went wrong. Please try again.";
        }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
    }

    const handleChat = () => {
        userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
        if(!userMessage) return;

        // Clear the input textarea and set its height to default
        chatInput.value = "";
        chatInput.style.height = `${inputInitHeight}px`;

        // Append the user's message to the chatbox
        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
        
        setTimeout(() => {
            // Display "Thinking..." message while waiting for the response
            const incomingChatLi = createChatLi("Thinking...", "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            generateResponse(incomingChatLi);
        }, 600);
    }

    chatInput.addEventListener("input", () => {
        // Adjust the height of the input textarea based on its content
        chatInput.style.height = `${inputInitHeight}px`;
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    chatInput.addEventListener("keydown", (e) => {
        // If Enter key is pressed without Shift key and handle the chat
        if(e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleChat();
        }
    });

    sendChatBtn.addEventListener("click", handleChat);
});
