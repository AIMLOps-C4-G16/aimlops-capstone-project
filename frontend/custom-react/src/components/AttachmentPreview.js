import React from 'react';

function AttachmentPreview({ file }) {
  if (!file) return null;

  // Handle restored file data (from localStorage)
  if (file.isRestored) {
    return (
      <div className="attachment-preview">
        <div className="restored-file-info">
          <div className="file-icon">📷</div>
          <div className="file-details">
            <div className="file-name">{file.name}</div>
            <div className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
            <div className="restored-note">(Previously uploaded image)</div>
          </div>
        </div>
      </div>
    );
  }

  // Handle actual File objects
  if (file instanceof File) {
    const imageUrl = URL.createObjectURL(file);

    return (
      <div className="attachment-preview">
        <img 
          src={imageUrl} 
          alt="Preview" 
          className="preview-image"
          onLoad={() => {
            // Clean up the object URL after the image loads
            setTimeout(() => URL.revokeObjectURL(imageUrl), 1000);
          }}
        />
      </div>
    );
  }

  // Fallback for non-File objects
  return (
    <div className="attachment-preview">
      <div className="restored-file-info">
        <div className="file-icon">📷</div>
        <div className="file-details">
          <div className="file-name">{file.name || 'Unknown file'}</div>
          <div className="file-size">{file.size ? (file.size / 1024 / 1024).toFixed(2) + ' MB' : 'Unknown size'}</div>
          <div className="restored-note">(Previously uploaded image)</div>
        </div>
      </div>
    </div>
  );
}

export default AttachmentPreview;
