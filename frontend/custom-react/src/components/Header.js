import React from 'react';

function Header({ user, onLogout, onClearHistory, onAvatarClick, showUserMenu, userMenuRef }) {
  return (
    <header className="header">
      <div className="header-content">
        <h1>AI Image Assistant</h1>
        <div className="user-section" ref={userMenuRef}>
          <div className="user-info" onClick={onAvatarClick}>
            <img 
              src={user.picture} 
              alt={user.name} 
              className="user-avatar"
            />
            <span className="user-name">{user.name}</span>
          </div>
          {showUserMenu && (
            <div className="user-menu">
              <div className="user-menu-item">
                <span>Email: {user.email}</span>
              </div>
              <div className="user-menu-item">
                <button onClick={onClearHistory} className="clear-history-btn">
                  Clear History
                </button>
              </div>
              <div className="user-menu-item">
                <button onClick={onLogout} className="logout-btn">
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
