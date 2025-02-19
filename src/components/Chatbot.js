import React, { useState } from "react";

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const handleSend = async (e) => {
    if (input.trim() === "") return;

    const newMessages = [...messages, { text: input, user: "You" }];
    setMessages(newMessages);
    setInput("");

    const res = await fetch('http://localhost:5000/ask', {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({  text: input }),
    });
    const text = await res.text();

    setTimeout(() => {
      const botResponse = { text: text, user: "Bot" };
      setMessages([...newMessages, botResponse]);
    }, 1000);
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.user === "You" ? "user-message" : "bot-message"}`}>
            <strong>{msg.user}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask your fantasy football question..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default Chatbot;
