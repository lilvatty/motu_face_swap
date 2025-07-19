export default function StartButton({ text, onClick }) {
  return (
    <button
      className="main-button w-3/5 height-input rounded-4xl transition-all"
      onClick={onClick}
    >
      {text}
    </button>
  );
}
