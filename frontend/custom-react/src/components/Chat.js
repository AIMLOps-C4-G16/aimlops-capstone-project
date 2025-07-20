import React from 'react';
import AttachmentPreview from './AttachmentPreview';

function Chat({ model, messages }) {
  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            {message.type === 'user' && (
              <div className="user-message">
                <span>{message.text}</span>
              </div>
            )}
            
            {message.type === 'system' && (
              <div className="system-message">
                <span>{message.text}</span>
              </div>
            )}
            
            {message.type === 'caption' && (
              <div className="caption-message">
                {message.files ? (
                  // Multiple files display
                  <div className="multiple-files-preview">
                    <h4>Uploaded Images ({message.files.length}):</h4>
                    <div className="files-grid">
                      {message.files.map((file, idx) => (
                        <div key={idx} className="file-preview-item">
                          <AttachmentPreview file={file} />
                          <div className="file-name">{file.name}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  // Single file display (backward compatibility)
                  <AttachmentPreview file={message.file} />
                )}
                <div className="captions">
                  <h4>Generated Captions:</h4>
                  <ul>
                    {message.captions.map((caption, idx) => (
                      <li key={idx}>{caption}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
            
            {message.type === 'similar' && (
              <div className="similar-message">
                <AttachmentPreview file={message.file} />
                <div className="similar-images">
                  <h4>Similar Images:</h4>
                  <div className="image-grid">
                    {message.images.map((image, idx) => (
                      <img key={idx} src={image} alt={`Similar ${idx + 1}`} />
                    ))}
                  </div>
                </div>
              </div>
            )}
            
            {message.type === 'search' && (
              <div className="search-message">
                <div className="search-query">
                  <h4>Search: "{message.text}"</h4>
                </div>
                <div className="search-results">
                  <h4>Results:</h4>
                  <div className="image-grid">
                    {message.images.map((image, idx) => (
                      <img key={idx} src={image} alt={`Result ${idx + 1}`} />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Chat;
