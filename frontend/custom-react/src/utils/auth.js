// Auth utility functions for managing user data in localStorage

export const saveUser = (user) => {
  try {
    localStorage.setItem('user', JSON.stringify(user));
  } catch (error) {
    console.error('Error saving user to localStorage:', error);
  }
};

export const loadUser = () => {
  try {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error('Error loading user from localStorage:', error);
    return null;
  }
};

export const clearUser = () => {
  try {
    localStorage.removeItem('user');
  } catch (error) {
    console.error('Error clearing user from localStorage:', error);
  }
};

// Chat history utility functions for managing user chat data in localStorage

export const saveChatHistory = (userEmail, messages) => {
  try {
    const key = `chat_history_${userEmail}`;
    // Convert File objects to serializable format
    const serializableMessages = messages.map(message => {
      if (message.type === 'caption' || message.type === 'similar') {
        // Convert File object to base64 string for storage
        return {
          ...message,
          file: message.file ? {
            name: message.file.name,
            size: message.file.size,
            type: message.file.type,
            lastModified: message.file.lastModified
          } : null
        };
      }
      return message;
    });
    localStorage.setItem(key, JSON.stringify(serializableMessages));
  } catch (error) {
    console.error('Error saving chat history to localStorage:', error);
  }
};

export const loadChatHistory = (userEmail) => {
  try {
    const key = `chat_history_${userEmail}`;
    const historyData = localStorage.getItem(key);
    if (historyData) {
      const messages = JSON.parse(historyData);
      // Convert stored file metadata back to a format that can be displayed
      return messages.map(message => {
        if (message.type === 'caption' || message.type === 'similar') {
          return {
            ...message,
            file: message.file ? {
              name: message.file.name,
              size: message.file.size,
              type: message.file.type,
              lastModified: message.file.lastModified,
              // Add a flag to indicate this is restored data
              isRestored: true
            } : null
          };
        }
        return message;
      });
    }
    return [];
  } catch (error) {
    console.error('Error loading chat history from localStorage:', error);
    return [];
  }
};

export const clearChatHistory = (userEmail) => {
  try {
    const key = `chat_history_${userEmail}`;
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Error clearing chat history from localStorage:', error);
  }
};

export const clearAllChatHistory = () => {
  try {
    // Remove all chat history keys
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('chat_history_')) {
        localStorage.removeItem(key);
      }
    });
  } catch (error) {
    console.error('Error clearing all chat history from localStorage:', error);
  }
};

// Debug function to check localStorage state
export const debugLocalStorage = () => {
  try {
    const keys = Object.keys(localStorage);
    const chatHistoryKeys = keys.filter(key => key.startsWith('chat_history_'));
    console.log('Current localStorage state:');
    console.log('All keys:', keys);
    console.log('Chat history keys:', chatHistoryKeys);
    chatHistoryKeys.forEach(key => {
      const data = localStorage.getItem(key);
      console.log(`${key}:`, data ? JSON.parse(data).length + ' messages' : 'empty');
    });
  } catch (error) {
    console.error('Error debugging localStorage:', error);
  }
};
