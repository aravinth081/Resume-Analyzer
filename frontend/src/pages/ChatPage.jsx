import { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';
import { Send, Bot, User, Sparkles } from 'lucide-react';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    chatAPI.history().then(r => setMessages(r.data || [])).catch(() => {});
  }, []);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const send = async () => {
    if (!input.trim() || sending) return;
    const msg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: msg }]);
    setSending(true);
    try {
      const res = await chatAPI.send(msg);
      setMessages(prev => [...prev, res.data]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }]);
    } finally { setSending(false); }
  };

  const quickActions = [
    'How to improve my resume?',
    'What skills should I learn?',
    'What is my ATS score?',
    'How to prepare for interviews?',
  ];

  return (
    <div className="chat-page">
      <div className="chat-header">
        <Bot size={24} /> <h1>AI Career Copilot</h1>
        <span className="chat-badge"><Sparkles size={14} /> Powered by AI</span>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <Bot size={48} className="chat-empty-icon" />
            <h2>How can I help you today?</h2>
            <p>Ask me about your resume, skills, career advice, or interview prep.</p>
            <div className="quick-actions">
              {quickActions.map((q, i) => (
                <button key={i} onClick={() => { setInput(q); }} className="quick-btn">{q}</button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role}`}>
            <div className="msg-avatar">{m.role === 'user' ? <User size={18} /> : <Bot size={18} />}</div>
            <div className="msg-content"><pre>{m.content}</pre></div>
          </div>
        ))}
        {sending && (
          <div className="chat-msg assistant">
            <div className="msg-avatar"><Bot size={18} /></div>
            <div className="msg-content typing"><span></span><span></span><span></span></div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-bar">
        <input type="text" placeholder="Ask me anything about your career..." value={input}
          onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()} disabled={sending} />
        <button onClick={send} disabled={!input.trim() || sending} className="send-btn">
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}
