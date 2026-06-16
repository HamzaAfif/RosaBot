// The text field + send button. State lives in App; this receives it via props.
function InputBar({ input, setInput, onSend, disabled }) {
  return (
    <div className="flex gap-2.5 border-t border-[#ece0d8] bg-[var(--paper)] px-4 pb-[18px] pt-3.5">
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSend()}
        placeholder="Ask about a dish, cocktail, or allergen…"
        disabled={disabled}
        className="flex-1 rounded-[26px] border border-[#ece0d8] bg-[var(--cream)] px-[18px] py-3 text-[14.5px] text-[var(--ink)] outline-none transition focus:border-[var(--rosa)] focus:bg-white"
      />
      <button
        onClick={onSend}
        disabled={disabled}
        aria-label="Send"
        className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[var(--rosa-bright)] to-[var(--rosa-deep)] text-lg text-white shadow-[0_4px_14px_rgba(168,18,58,0.3)] transition hover:-translate-y-0.5 hover:scale-105 active:scale-95 disabled:translate-y-0 disabled:opacity-45"
      >
        ➤
      </button>
    </div>
  );
}

export default InputBar;