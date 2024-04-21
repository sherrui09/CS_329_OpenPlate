const chatbox = document.querySelector(".chatbox");

$(document).ready(function() {
    $('#user-input').keypress(function(e) {
        if (e.which == 13) {  // Enter key pressed
            sendMessage();
            e.preventDefault(); // Prevent form submit
        }
    });

    startChat();
});

function startChat() {
    $.getJSON('/start', function(data) {
        // Append bot messages with a specific class
        appendBotMessage(data.message);
        appendBotMessage(data.question);
    });
}

function appendBotMessage(message) {
    $('#messages').append(`<div class="bot-message">${message}</div>`);
    scrollToBottom();
}

function sendMessage() {
    const userInput = $('#user-input').val();
    $('#user-input').val(''); // Clear input field
    if (!userInput.trim()) return; // Do nothing if the input is only spaces

    // Append user message with a specific class
    $('#messages').append(`<div class="user-message">${userInput}</div>`);
    scrollToBottom();

    $.ajax({
        url: '/message',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({message: userInput}),
        success: function(data) {
            // Append bot message with a specific class
            appendBotMessage(data.message);
            if (data.message.includes("Here's your profile")) {
                // $('#user-input').prop('disabled', true); // Optionally disable input if conversation ends
            }
        },
        error: function() {
            // Append error message with a specific class
            $('#messages').append(`<div class="error-message">There was an error processing your message. Please try again.</div>`);
        }
    });
}

function scrollToBottom() {
    var messagesContainer = $('#messages');
    messagesContainer.scrollTop(messagesContainer.prop("scrollHeight"));
}
