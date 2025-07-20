import React, { useState, useRef } from 'react';

function BottomBar({ 
  searchText, 
  onSearchTextChange, 
  attachmentType, 
  imageFiles, 
  onFileChange, 
  onRemoveAttachment, 
  onSend, 
  loading
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);
  const textAreaRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    setDragCounter(prev => prev + 1);
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragCounter(prev => prev - 1);
    if (dragCounter <= 1) {
      setIsDragOver(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    setDragCounter(0);

    const files = Array.from(e.dataTransfer.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length > 0) {
      // Create a custom event to simulate file input change
      const customEvent = {
        target: {
          files: imageFiles,
          getAttribute: () => 'mixed' // Indicate mixed content (text + images)
        }
      };
      onFileChange(customEvent);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const handleAttachmentClick = () => {
    fileInputRef.current.click();
  };

  const handleFileInputChange = (e) => {
    const files = Array.from(e.target.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length > 0) {
      const customEvent = {
        target: {
          files: imageFiles,
          getAttribute: () => 'mixed'
        }
      };
      onFileChange(customEvent);
    }
    
    // Reset the input value so the same file can be selected again
    e.target.value = '';
  };

  return (
    <div className="bottom-bar">
      <div className="input-container">
        <div 
          className={`text-input-wrapper ${isDragOver ? 'drag-over' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="textarea-container">
            <textarea
              ref={textAreaRef}
              value={searchText}
              onChange={onSearchTextChange}
              onKeyPress={handleKeyPress}
              placeholder="Enter your search query or drag & drop images here..."
              className="search-input"
              disabled={loading}
              rows={3}
            />
            
            <div className="inline-buttons">
              <button 
                onClick={handleAttachmentClick}
                className="attachment-btn"
                disabled={loading}
                title="Attach images"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
                </svg>
              </button>
              
              <button 
                onClick={onSend} 
                disabled={loading || (!searchText && imageFiles.length === 0)}
                className="send-btn-inline"
                title="Send message"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
          
          {isDragOver && (
            <div className="drag-overlay">
              <div className="drag-message">
                Drop images here to upload
              </div>
            </div>
          )}
        </div>
        
        {/* Hidden file input for attachment button */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />
        
        {imageFiles.length > 0 && (
          <div className="attachments-container">
            <div className="attachments-header">
              <span>{imageFiles.length} image(s) selected</span>
              <button 
                onClick={() => onRemoveAttachment()} 
                className="remove-all-btn"
                disabled={loading}
              >
                Remove All
              </button>
            </div>
            <div className="attachments-grid">
              {imageFiles.map((file, index) => (
                <div key={index} className="attachment-item">
                  {file instanceof File ? (
                    <img 
                      src={URL.createObjectURL(file)} 
                      alt={`Preview ${index + 1}`} 
                      className="attachment-preview"
                    />
                  ) : (
                    <div className="attachment-preview">
                      <div className="restored-file-info">
                        <div className="file-icon">📷</div>
                        <div className="file-details">
                          <div className="file-name">{file.name}</div>
                          <div className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div className="attachment-info">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                  <button 
                    onClick={() => onRemoveAttachment(index)} 
                    className="remove-single-btn"
                    disabled={loading}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BottomBar;
