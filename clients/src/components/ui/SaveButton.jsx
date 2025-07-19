export default function SaveButton({ text, onClick, isDisabled }) {
  return (
    <button
      className={`border-2 border-[#002448] w-4/5 height-input rounded-3xl transition-all main-button mt-[52px] ${isDisabled ? "opacity-50 cursor-not-allowed" : ""}`}
      onClick={onClick}
      disabled={isDisabled}
    >
      {text}
    </button>
  );
}
