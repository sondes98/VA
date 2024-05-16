import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import "./App.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faShoppingBag } from '@fortawesome/free-solid-svg-icons';

function App() {
  const [conversation, setConversation] = useState([]);
  const [error, setError] = useState('');
  const [interactionStarted, setInteractionStarted] = useState(false);
  const [assistantSpeaking, setAssistantSpeaking] = useState(false);
  const [userSpeaking, setUserSpeaking] = useState(false);
  const [bagItems, setBagItems] = useState([]);
  const chatboxRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);

  useEffect(() => {
    if (interactionStarted && !assistantSpeaking && !userSpeaking) {
      handleNextMessage();
    }
  }, [conversation, assistantSpeaking, userSpeaking]);

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const scrollToBottom = () => {
    chatboxRef.current.scrollTop = chatboxRef.current.scrollHeight;
  };

  const speak = (text) => {
    return new Promise((resolve) => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.8;
      utterance.onstart = () => setUserSpeaking(false);
      utterance.onend = () => {
        setAssistantSpeaking(false);
        resolve();
      };
      synthRef.current.cancel(); // Cancel any ongoing speech before starting a new one
      synthRef.current.speak(utterance);
      setAssistantSpeaking(true);
      addToConversation({ text, speaker: 'assistant' });
    });
  };

  const addToConversation = (message) => {
    setConversation((prevConversation) => [...prevConversation, message]);
  };

  const handleNextMessage = async () => {
    const lastMessage = conversation[conversation.length - 1];
    if (lastMessage && lastMessage.speaker === 'assistant') {
      setUserSpeaking(true);
      setAssistantSpeaking(false);
      try {
        const speechResult = await listenForSpeech();
        setUserSpeaking(false);
        addToConversation({ text: speechResult, speaker: 'user' });
        handleUserResponse(speechResult);
      } catch (error) {
        console.error('Speech recognition error:', error);
        setUserSpeaking(false);
      }
    } else if (lastMessage && lastMessage.speaker === 'user') {
      setUserSpeaking(false);
      setAssistantSpeaking(true);
    }
  };

  const handleStartInteraction = async () => {
    setInteractionStarted(true);
    await speak("Hello, I'm Hypia. I'm here to help you find your future laptop.");
    await speak("What brand are you looking for?");
  };

  const handleUserResponse = async (speechResult) => {
    let laptops = []; // Declare laptops variable here
    const lastMessage = conversation[conversation.length - 1];
    if (lastMessage && lastMessage.text.includes("What brand are you looking for?")) {
      await speak("What is your maximum budget in euros?");
    } else if (lastMessage && lastMessage.text.includes("maximum budget")) {
      const brandInput = conversation[conversation.length - 2].text;
      const priceInput = speechResult;
      try {
        const response = await axios.post('http://127.0.0.1:5000/assistant', { brand: brandInput, price: priceInput });
        const responseData = response.data;
        if (responseData.error) {
          setError(responseData.error);
          return;
        }
        if (responseData.laptops && responseData.laptops.length > 0) {
          laptops = responseData.laptops; // Assign value to laptops here
          await speak("Here are the laptops that match your criteria:");
          for (let index = 0; index < laptops.length; index++) {
            const laptop = laptops[index];
            await speak(`${index + 1}. ${laptop.Product}, ${laptop.Price} euros`);
          }
          await speak("Please choose a laptop by saying its number or position, like 'the first one', 'the second one', etc.");
          setUserSpeaking(true);
          try {
            const choiceSpeechResult = await listenForSpeech();
            setUserSpeaking(false);
            handleUserChoice(choiceSpeechResult, laptops);
          } catch (error) {
            console.error('Speech recognition error:', error);
            setUserSpeaking(false);
          }
        } else {
          await speak("Sorry, no laptops matching your criteria were found.");
          setUserSpeaking(false);
        }
      } catch (error) {
        setError("An error occurred. Please try again later.");
        console.error('Error:', error);
      }
    }
  };
  
  const handleUserChoice = async (speechResult, laptops) => {
    const choiceWords = speechResult.toLowerCase().split(" ");
    console.log("Choice Words:", choiceWords);
    const choiceOrdinal = choiceWords.find(word => ordinalToNumber(word) !== -1);
    const choiceIndex = ordinalToNumber(choiceOrdinal) - 1;
    console.log("Choice Index:", choiceIndex);
    console.log("Laptops length:", laptops.length);
    if (!isNaN(choiceIndex) && choiceIndex >= 0 && choiceIndex < laptops.length) {
      const chosenLaptop = laptops[choiceIndex];
      setBagItems(prevBagItems => [...prevBagItems, chosenLaptop]);
      await speak(`Your ${chosenLaptop.Product} laptop is added to your bag. Please check it and complete your payment process.`);
      try {
        await axios.post('http://localhost:5000/add-to-bag', chosenLaptop);
      } catch (error) {
        console.error('Failed to send laptop to backend:', error);
      }
    } else {
      await speak("Invalid choice. Please choose a valid laptop number or position.");
      }
    
  };


  const ordinalToNumber = (ordinal) => {
    switch (ordinal.toLowerCase()) {
      case 'first': return 1;
      case 'second': return 2;
      case 'third': return 3;
      case 'fourth': return 4;
      case 'fifth': return 5;
      case 'sixth': return 6;
      case 'seventh': return 7;
      case 'eighth': return 8;
      case 'ninth': return 9;
      case 'tenth': return 10;
      default: return -1; // Invalid ordinal
    }
  };
  
  
  


  const listenForSpeech = async () => {
    return new Promise((resolve, reject) => {
      const recognition = new window.webkitSpeechRecognition();
      recognition.lang = 'en-US';
      recognition.start();
      recognition.onresult = (event) => {
        const speechResult = event.results[0][0].transcript;
        resolve(speechResult);
      };
      recognition.onerror = (event) => {
        reject(event.error);
      };
    });
  };

  return (
    <div className={`container ${interactionStarted ? 'interaction-started' : ''}`}>
      {!interactionStarted && (
        <div className="interaction-btn" onClick={handleStartInteraction}>
          Start Interaction
        </div>
      )}
      {error && <p>{error}</p>}
      <div className='chatbox' ref={chatboxRef}>
        {conversation.map((message, index) => (
          <div key={index} className={`message ${message.speaker}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div>
        <FontAwesomeIcon icon={faShoppingBag} />
        <ul>
          {bagItems.map((item, index) => (
            <li key={index}>{item.Product}</li>
          ))}
        </ul>
      </div>
      
    </div>
  );
}

export default App;
