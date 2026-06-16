import { useState, useRef, useEffect } from "react";
import MessageBubble from "./components/MessageBubble";
import TypingIndicator from "./components/TypingIndicator";
import InputBar from "./components/InputBar";
import "./index.css";

const STARTERS = [
  "Does the Pisco Sour have egg?",
  "What cocktails do you have?",
  "Anything without dairy?",
  "How is the Amaretto Sour made?",
];

function App() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Bonjour! I'm RosaBot 🌹 — your service-floor sidekick at India Rosa. Ask me about any dish, cocktail spec, ingredient, or allergen." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId] = useState(
    () => "web-" + Math.random().toString(36).slice(2, 10)
  );

  // Auto-scroll to the newest message.
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text) {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, conversation_id: conversationId }),
      });
      if (!res.ok) throw new Error("Server " + res.status);
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "bot", text: data.reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ I couldn't reach the kitchen just now. Make sure the backend is running, then try again." },
      ]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const showChips = messages.length === 1 && !loading;

  return (
    <div className="relative z-10 flex h-[min(86vh,760px)] w-full max-w-[460px] flex-col overflow-hidden rounded-3xl border border-[rgba(201,162,75,0.25)] bg-[var(--cream)] shadow-[0_24px_70px_-20px_rgba(110,12,38,0.35)] animate-rise max-[520px]:h-screen max-[520px]:rounded-none max-[520px]:border-0">
      {/* Header */}
      <header className="relative flex items-center gap-3.5 overflow-hidden bg-gradient-to-br from-[var(--rosa)] to-[var(--rosa-deep)] px-6 py-5 text-white">
        <div className="absolute -right-8 -top-8 h-36 w-36 rounded-full bg-[radial-gradient(circle,rgba(201,162,75,0.35),transparent_70%)]" />
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border-2 border-[var(--gold)] bg-[var(--cream)] text-2xl shadow-lg">
          🌹
        </div>
        <div className="z-10">
          <h1 className="font-display text-2xl font-semibold leading-none">RosaBot</h1>
          <span className="text-xs font-light uppercase tracking-[2.5px] opacity-80">India Rosa</span>
        </div>
        <div className="z-10 ml-auto flex items-center gap-2 text-[11px] opacity-85">
          <span className="h-2 w-2 rounded-full bg-[#6ee29a] animate-pulse-dot" /> online
        </div>
      </header>

      {/* Messages */}
      <div className="messages-scroll flex flex-1 flex-col gap-3.5 overflow-y-auto px-4 pt-5 pb-2">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Suggested chips (only before first question) */}
      {showChips && (
        <div className="flex flex-wrap gap-2 px-4 pb-3.5">
          {STARTERS.map((q, i) => (
            <button
              key={q}
              onClick={() => send(q)}
              style={{ animationDelay: `${i * 0.06}s` }}
              className="animate-pop rounded-full border border-[rgba(168,18,58,0.3)] px-3.5 py-1.5 text-[12.5px] text-[var(--rosa-deep)] transition hover:-translate-y-px hover:border-[var(--rosa)] hover:bg-[var(--rosa)] hover:text-white"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      <InputBar input={input} setInput={setInput} onSend={() => send()} disabled={loading} />
    </div>
  );
}

export default App;