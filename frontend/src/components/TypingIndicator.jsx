// The three bouncing dots shown while RosaBot is thinking.
function TypingIndicator() {
  return (
    <div className="flex max-w-[84%] animate-pop items-center gap-1 self-start rounded-[18px_18px_18px_5px] border border-[#ece0d8] bg-[var(--paper)] px-4 py-3.5 shadow-[0_2px_10px_rgba(110,12,38,0.05)]">
      <span className="h-[7px] w-[7px] animate-blink rounded-full bg-[var(--rosa)]" />
      <span className="h-[7px] w-[7px] animate-blink rounded-full bg-[var(--rosa)]" style={{ animationDelay: "0.2s" }} />
      <span className="h-[7px] w-[7px] animate-blink rounded-full bg-[var(--rosa)]" style={{ animationDelay: "0.4s" }} />
    </div>
  );
}

export default TypingIndicator;