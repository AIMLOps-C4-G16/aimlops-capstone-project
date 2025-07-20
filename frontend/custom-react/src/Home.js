import React, { useState, useRef, useEffect } from 'react';
import { GoogleLogin, googleLogout } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import Header from './components/Header';
import Chat from './components/Chat';
import BottomBar from './components/BottomBar';
import { getCaption, getMultipleCaptions, searchSimilar, searchMultipleSimilar, searchImages, validateImageFile } from './services/api';
import { saveUser, loadUser, clearUser, saveChatHistory, loadChatHistory, clearChatHistory, debugLocalStorage } from './utils/auth';
import './App.css';

function Home() {
  const [user, setUser] = useState(null);
  const [model, setModel] = useState('model-a'); // Set default model
  const [searchText, setSearchText] = useState('');
  const [attachmentType, setAttachmentType] = useState(null);
  const [imageFiles, setImageFiles] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef();

  useEffect(() => {
    // Restore user from localStorage only on initial load
    const stored = loadUser();
    if (stored) {
      setUser(stored);
      // Load chat history for the user
      const history = loadChatHistory(stored.email);
      setMessages(history);
    }
  }, []); // Empty dependency array ensures this only runs once on mount

  useEffect(() => {
    function handleClickOutside(event) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    }
    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showUserMenu]);

  // Save chat history whenever messages change
  useEffect(() => {
    if (user && messages.length > 0) {
      console.log('Saving', messages.length, 'messages for user:', user.email);
      saveChatHistory(user.email, messages);
      debugLocalStorage();
    }
  }, [messages, user]);

  const handleLoginSuccess = (credentialResponse) => {
    const decoded = jwtDecode(credentialResponse.credential);
    const userObj = {
      name: decoded.name,
      email: decoded.email,
      picture: decoded.picture,
      loginTime: Date.now()
    };
    
    console.log('User logging in:', userObj.email);
    
    // Clear current UI state (but keep localStorage data intact)
    setMessages([]);
    setImageFiles([]);
    setAttachmentType(null);
    setSearchText('');
    
    // Set new user
    setUser(userObj);
    saveUser(userObj);
    
    // Load the new user's chat history (preserves other users' data)
    const history = loadChatHistory(userObj.email);
    console.log('Loaded history for', userObj.email, ':', history.length, 'messages');
    setMessages(history);
    
    // Debug localStorage state
    debugLocalStorage();
  };

  const handleLogout = () => {
    googleLogout();
    // Don't clear chat history - keep it in localStorage for future logins
    // Only clear the current user session
    setUser(null);
    setShowUserMenu(false);
    clearUser();
    setMessages([]);
    setImageFiles([]);
    setAttachmentType(null);
    setSearchText('');
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      try {
        // Validate all files
        files.forEach(file => validateImageFile(file));
        
        // Add new files to existing ones
        setImageFiles(prevFiles => [...prevFiles, ...files]);
        
        // Determine attachment type based on context
        const attachmentType = e.target.getAttribute('data-type') || 'mixed';
        setAttachmentType(attachmentType);
      } catch (error) {
        alert(error.message);
      }
    }
  };

  const handleSearchTextChange = (e) => setSearchText(e.target.value);
  
  const handleRemoveAttachment = (indexToRemove) => {
    if (indexToRemove !== undefined) {
      // Remove specific file
      setImageFiles(prevFiles => prevFiles.filter((_, index) => index !== indexToRemove));
    } else {
      // Remove all files
      setImageFiles([]);
      setAttachmentType(null);
    }
  };

  const handleClearHistory = () => {
    if (user) {
      // Only clear the current user's chat history
      clearChatHistory(user.email);
      setMessages([]);
      setShowUserMenu(false);
      console.log('Cleared chat history for user:', user.email);
      debugLocalStorage();
    }
  };

  const handleSend = async () => {
    if (loading) return;
    setLoading(true);
    try {
      if (imageFiles.length > 0 && searchText) {
        // Check if the text indicates a similar search request
        const isSimilarSearch = searchText.toLowerCase().includes('find similar') || 
                               searchText.toLowerCase().includes('similar') ||
                               searchText.toLowerCase().includes('find like') ||
                               searchText.toLowerCase().includes('look like');
        
        if (isSimilarSearch) {
          // Similar search request with images
          setMessages((msgs) => [
            ...msgs,
            { type: 'user', text: `"${searchText}" with ${imageFiles.length} uploaded image(s).` }
          ]);
          
          // Process all images for similar search using multiple file API
          const res = await searchMultipleSimilar(imageFiles, model);
          const results = res.results || [res]; // Handle both new and old API formats
          
          // Add similar search messages for each image
          results.forEach((result, index) => {
            // Use the original File object from imageFiles array
            const originalFile = imageFiles[index];
            const images = result.images || result.data || [
              'https://placekitten.com/200/200',
              'https://placekitten.com/201/200',
              'https://placekitten.com/202/200',
            ];
            setMessages((msgs) => [
              ...msgs,
              { type: 'similar', file: originalFile, images },
            ]);
          });
        } else {
          // Regular caption request with images
          setMessages((msgs) => [
            ...msgs,
            { type: 'user', text: `"${searchText}" with ${imageFiles.length} uploaded image(s).` }
          ]);
          
          // Process all images for captions using multiple file API
          const res = await getMultipleCaptions(imageFiles, model);
          
          // Get the combined caption response
          const captions = res.captions || res.data || ['A collection of beautiful images with diverse content.'];
          
          // Create a single caption message for all images
          setMessages((msgs) => [
            ...msgs,
            { 
              type: 'caption', 
              files: imageFiles, // Pass all files
              captions: captions 
            },
          ]);
        }
        
        setImageFiles([]);
        setAttachmentType(null);
        setSearchText('');
      } else if (imageFiles.length > 0 && !searchText) {
        // Images only - treat as similar image search for all images
        setMessages((msgs) => [
          ...msgs,
          { type: 'user', text: `Uploaded ${imageFiles.length} image(s) to search similar.` }
        ]);
        
        // Process all images for similar search using multiple file API
        const res = await searchMultipleSimilar(imageFiles, model);
        const results = res.results || [res]; // Handle both new and old API formats
        
        // Add similar search messages for each image
        results.forEach((result, index) => {
          // Use the original File object from imageFiles array
          const originalFile = imageFiles[index];
          const images = result.images || result.data || [
            'https://placekitten.com/200/200',
            'https://placekitten.com/201/200',
            'https://placekitten.com/202/200',
          ];
          setMessages((msgs) => [
            ...msgs,
            { type: 'similar', file: originalFile, images },
          ]);
        });
        
        setImageFiles([]);
        setAttachmentType(null);
      } else if (imageFiles.length === 0 && searchText) {
        // Text only - treat as image search
        setMessages((msgs) => [
          ...msgs,
          { type: 'user', text: searchText }
        ]);
        const res = await searchImages(searchText, model);
        const images = res.images || res.data || [
          'https://placekitten.com/210/200',
          'https://placekitten.com/211/200',
          'https://placekitten.com/212/200',
        ];
        setMessages((msgs) => [
          ...msgs,
          { type: 'search', text: searchText, images },
        ]);
        setSearchText('');
      } else {
        alert('Please enter text or upload an image.');
      }
    } catch (err) {
      alert('Error communicating with API');
    }
    setLoading(false);
  };

  if (!user) {
    return (
      <div className="login-container">
        <h2>Login with Google</h2>
        <GoogleLogin onSuccess={handleLoginSuccess} onError={() => alert('Login Failed')} />
      </div>
    );
  }

  return (
    <div className="main-app-container">
      <Header
        user={user}
        onLogout={handleLogout}
        onClearHistory={handleClearHistory}
        onAvatarClick={() => setShowUserMenu((v) => !v)}
        showUserMenu={showUserMenu}
        userMenuRef={userMenuRef}
      />
      <Chat
        model={model}
        messages={messages}
      />
      <BottomBar
        searchText={searchText}
        onSearchTextChange={handleSearchTextChange}
        attachmentType={attachmentType}
        imageFiles={imageFiles}
        onFileChange={handleFileChange}
        onRemoveAttachment={handleRemoveAttachment}
        onSend={handleSend}
        loading={loading}
      />
    </div>
  );
}

export default Home; 