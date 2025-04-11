// Generate a unique session ID for this chat
const sessionId = 'session_' + Math.random().toString(36).substring(2, 15);
        
// DOM elements
const chatButton = document.getElementById('chatButton');
const chatDialog = document.getElementById('chatDialog');
const chatClose = document.getElementById('chatClose');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSend = document.getElementById('chatSend');
const typingIndicator = document.getElementById('typingIndicator');

// Open chat dialog
chatButton.addEventListener('click', () => {
    chatDialog.classList.add('open');
    chatInput.focus();
});

// Close chat dialog
chatClose.addEventListener('click', () => {
    chatDialog.classList.remove('open');
});

// Send message when pressing Enter
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && chatInput.value.trim() !== '') {
        sendMessage();
    }
});

// Send message on button click
chatSend.addEventListener('click', () => {
    if (chatInput.value.trim() !== '') {
        sendMessage();
    }
});

// Function to send message
function sendMessage() {
    const message = chatInput.value.trim();
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    chatInput.value = '';
    
    // Show typing indicator
    typingIndicator.style.display = 'block';
    
    // Call API to get response
    fetchAIResponse(message);
}

// Function to add a message to the chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'ai-message');
    messageDiv.textContent = text;
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

    // Function to fetch AI response from backend
async function fetchAIResponse(message) {
  try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 60 seconds timeout

      const response = await fetch('https://4b49-34-125-25-0.ngrok-free.app/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
              message: message,
              session_id: sessionId,
          }),
          signal: controller.signal
      });

      clearTimeout(timeoutId);
      
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Hide typing indicator
      typingIndicator.style.display = 'none';
      
      // Add AI response to chat
      if (data.response) {
          addMessage(data.response, 'ai');
      } else if (data.error) {
          addMessage('Error: ' + data.error, 'ai');
      } else {
          addMessage('Sorry, I could not generate a response.', 'ai');
      }
  } catch (error) {
      console.error("Error fetching AI response:", error);
      
      // Hide typing indicator
      typingIndicator.style.display = 'none';
      
      // Add error message to chat
      addMessage('Sorry, there was an error connecting to the AI.', 'ai');
  }
}