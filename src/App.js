import React, { useState, useEffect } from 'react';
import axios from 'axios';
import "./App.css"

function App() {
  const [conversation, setConversation] = useState([]);
  const [error, setError] = useState('');
  const [interactionStarted, setInteractionStarted] = useState(false);
  const [assistantSpeaking, setAssistantSpeaking] = useState(false);
  const [userSpeaking, setUserSpeaking] = useState(false);
  const [laptops, setLaptops] = useState([]);
  const [bagItems, setBagItems] = useState([]);

  useEffect(() => {
    if (interactionStarted && !assistantSpeaking && !userSpeaking) {
      handleNextMessage();
    }
  }, [conversation, assistantSpeaking, userSpeaking]);

  const speak = (text) => {
    return new Promise((resolve) => {
        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US'; // Set language to English (United States)
        utterance.onstart = () => {
            setUserSpeaking(false);
        };
        utterance.onend = () => {
            setAssistantSpeaking(false);
            resolve();
        };
        synth.speak(utterance);
        setAssistantSpeaking(true);
        addToConversation({ text, speaker: 'assistant' });
    });
};


  const addToConversation = (message) => {
    setConversation((prevConversation) => [...prevConversation, message]);
  };

  const handleNextMessage = async () => {
    const lastMessage = conversation[conversation.length - 1];
    if (lastMessage && lastMessage.speaker === 'user') {
      setAssistantSpeaking(true);
    } else if (lastMessage && lastMessage.speaker === 'assistant') {
      await handleAssistantSpeech();
    }
  };

  const handleStartInteraction = async () => {
    setInteractionStarted(true);
    await speak("What brand are you looking for?");
  };

  const handleAssistantSpeech = async () => {
    const lastMessage = conversation[conversation.length - 1];
    if (lastMessage && lastMessage.text === "What brand are you looking for?") {
      await speak("What is your maximum budget in euros?");
    }
  };

  const handleUserResponse = async (speechResult) => {
    const lastMessage = conversation[conversation.length - 1];
    if (lastMessage && lastMessage.text === "What brand are you looking for?") {
      await handleNextMessage();
    } else if (lastMessage && lastMessage.text.includes("maximum budget")) {
      const brandInput = conversation[conversation.length - 2].text;
      const priceInput = speechResult;
      try {
        const response = await axios.post('/assistant', { brand: brandInput, price: priceInput });
        const responseData = response.data;
        if (responseData.error) {
          setError(responseData.error);
          return;
        }
        if (responseData.laptops && responseData.laptops.length > 0) {
          setLaptops(responseData.laptops);
          await speak("Here are some laptops that match your criteria:");
          responseData.laptops.forEach((laptop, index) => {
            speak(`${index + 1}: ${laptop.Product} - ${laptop.Price} euros`);
          });
          await speak("Please choose a laptop by saying its position in the list.");
        } else {
          speak("Sorry, no laptops matching your criteria were found.");
        }
      } catch (error) {
        setError("An error occurred. Please try again later.");
        console.error('Error:', error);
      }
    } else if (lastMessage && lastMessage.text === "Please choose a laptop by saying its position in the list.") {
      const positionWords = speechResult.toLowerCase().split(" ");
      const numberWords = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"];
      let chosenPosition;
      positionWords.forEach((word, index) => {
        if (numberWords.includes(word)) {
          chosenPosition = index + 1;
        }
      });
      if (chosenPosition && chosenPosition <= laptops.length) {
        const chosenLaptop = laptops[chosenPosition - 1];
        setBagItems([...bagItems, chosenLaptop]);
        await speak(`Your laptop ${chosenLaptop.Product} is added to your bag. Please check your bag and complete the payment process. Thank you for asking me for help!`);
        setUserSpeaking(false);
      } else {
        await speak("Invalid position. Please choose a valid position in the list.");
      }
    }
  };

  const handleMicClick = async () => {
    if (!userSpeaking) {
      try {
        setAssistantSpeaking(false);
        setUserSpeaking(true);
        const speechResult = await listenForSpeech();
        setUserSpeaking(false);
        addToConversation({ text: speechResult, speaker: 'user' });
        handleUserResponse(speechResult);
      } catch (error) {
        console.error('Speech recognition error:', error);
        setUserSpeaking(false);
      }
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
    <div className='container'>
      <h1>Virtual Voice Assistant</h1>
      {!interactionStarted && <button onClick={handleStartInteraction}>Start Interaction</button>}
      {error && <p>{error}</p>}
      <div className='chatbox'>
        <h2>Conversation:</h2>
        {conversation.map((message, index) => (
          <div key={index} className={`message ${message.speaker}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div>
        <h2>Bag:</h2>
        <ul>
          {bagItems.map((item, index) => (
            <li key={index}>{item.Product}</li>
          ))}
        </ul>
      </div>
      <button onClick={handleMicClick} disabled={userSpeaking}>
        Speak
      </button>
      {assistantSpeaking && <p>Assistant is speaking...</p>}
      {userSpeaking && <p>Listening...</p>}
    </div>
  );
}

export default App;
