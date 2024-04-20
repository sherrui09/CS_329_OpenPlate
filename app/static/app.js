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
        $('#messages').append(`<div>Bot: ${data.message}</div>`);
        $('#messages').append(`<div>Bot: ${data.question}</div>`);
    });
}

function sendMessage() {
    const userInput = $('#user-input').val();
    $('#user-input').val(''); // Clear input field
    if (!userInput.trim()) return; // Do nothing if the input is only spaces

    $('#messages').append(`<div>User: ${userInput}</div>`); // Display user input in chat

    $.ajax({
        url: '/message',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({message: userInput}),
        success: function(data) {
            $('#messages').append(`<div>Bot: ${data.message}</div>`);
            if (data.message.includes("Here's your profile")) {
                $('#user-input').prop('disabled', true); // Optionally disable input if conversation ends
            }
            scrollToBottom(); // Scroll chat to the latest message
        },
        error: function() {
            $('#messages').append(`<div>Bot: There was an error processing your message. Please try again.</div>`);
            scrollToBottom(); // Scroll chat to the latest message
        }
    });
}

function scrollToBottom() {
    var messagesContainer = $('#messages');
    messagesContainer.scrollTop(messagesContainer.prop("scrollHeight"));
}
