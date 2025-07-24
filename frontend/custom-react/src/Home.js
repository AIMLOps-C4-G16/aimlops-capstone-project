import React, { useState, useRef, useEffect } from 'react';
import { GoogleLogin, googleLogout } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import Header from './components/Header';
import Chat from './components/Chat';
import BottomBar from './components/BottomBar';
import { getQuerySearch, getMultipleCaptions, searchMultipleSimilar, searchImages, validateImageFile } from './services/api';
import { saveUser, loadUser, clearUser, saveChatHistory, loadChatHistory, clearChatHistory, debugLocalStorage } from './utils/auth';
import './App.css';

function Home() {
  const [user, setUser] = useState(null);
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
    setMessages([]);
    setImageFiles([]);
    setAttachmentType(null);
    setSearchText('');
    setUser(userObj);
    saveUser(userObj);
    const history = loadChatHistory(userObj.email);
    setMessages(history);
    debugLocalStorage();
  };

  const handleLogout = () => {
    googleLogout();
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
        files.forEach(file => validateImageFile(file));
        setImageFiles(prevFiles => [...prevFiles, ...files]);
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
      setImageFiles(prevFiles => prevFiles.filter((_, index) => index !== indexToRemove));
    } else {
      setImageFiles([]);
      setAttachmentType(null);
    }
  };

  const handleClearHistory = () => {
    if (user) {
      clearChatHistory(user.email);
      setMessages([]);
      setShowUserMenu(false);
      debugLocalStorage();
    }
  };

  const handleSend = async () => {
    if (loading) return;
    setLoading(true);
    try {
      if (imageFiles.length > 0 ) {
        // If user enters text and uploads images, treat as similar search if text includes 'similar', else caption
        const isSimilarSearch = searchText.toLowerCase().includes('find similar') || 
                               searchText.toLowerCase().includes('similar') ||
                               searchText.toLowerCase().includes('find like') ||
                               searchText.toLowerCase().includes('look like');
        setMessages((msgs) => [
          ...msgs,
          { type: 'user', text: `"${searchText}" with ${imageFiles.length} uploaded image(s).` }
        ]);

        const res =await getQuerySearch(searchText, imageFiles);

        console.log('res==============', res)
        if(res.similar_images){
          setMessages((msgs) => [
            ...msgs,
            { type: 'similar', file: imageFiles[0], images: res.similar_images },
          ]);
        } else if(res.caption){
          setMessages((msgs) => [
            ...msgs,
            { type: 'caption', files: imageFiles, captions: res.caption },
          ]);
        } else if(res.index_response){
          setMessages((msgs) => [
            ...msgs,
            { type: 'index', file: imageFiles, indexResponse: res.index_response },
          ]);
        } else {
          setMessages((msgs) => [
            ...msgs,
            { type: 'system', text: 'No results found' },
          ]);
        }
        // if (isSimilarSearch) {
        //   // Similar search with images
        //   const similarIds = await searchMultipleSimilar(imageFiles);
        //   setMessages((msgs) => [
        //     ...msgs,
        //     { type: 'similar', file: imageFiles[0], images: similarIds },
        //   ]);
        // } else {
        //   // Captioning with images
        //   const captions = await getMultipleCaptions(imageFiles);
        //   setMessages((msgs) => [
        //     ...msgs,
        //     { type: 'caption', files: imageFiles, captions },
        //   ]);
        // }
        setImageFiles([]);
        setAttachmentType(null);
        setSearchText('');
      } else if (imageFiles.length === 0 && searchText) {
        // Text only - treat as image search
        setMessages((msgs) => [
          ...msgs,
          { type: 'user', text: searchText }
        ]);
        const similarIds = await searchImages(searchText);
        setMessages((msgs) => [
          ...msgs,
          { type: 'search', text: searchText, images: similarIds },
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