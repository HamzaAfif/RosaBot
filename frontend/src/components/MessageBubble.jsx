// Renders one chat bubble. Light **bold** formatting from the bot is supported.
function formatBold(text) {
  // Split on **...** and bold those segments. Safe: we map to elements, no innerHTML.
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="text-[var(--rosa-deep)]">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="max-w-[84%] animate-pop self-end rounded-[18px_18px_5px_18px] bg-gradient-to-br from-[var(--rosa-bright)] to-[var(--rosa)] px-4 py-3 text-[14.5px] leading-relaxed text-white shadow-[0_4px_14px_rgba(168,18,58,0.28)]">
        {message.text}
      </div>
    );
  }

  return (
    <div className="max-w-[84%] animate-pop self-start whitespace-pre-wrap rounded-[18px_18px_18px_5px] border border-[#ece0d8] bg-[var(--paper)] px-4 py-3 text-[14.5px] leading-relaxed text-[var(--ink)] shadow-[0_2px_10px_rgba(110,12,38,0.05)]">
      {formatBold(message.text)}
    </div>
  );
}

export default MessageBubble;