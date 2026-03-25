export default function StartButton({ text, onClick }) {
  return (
    <button
      className="main-button absolute bottom-50 w-2/5 height-input rounded-4xl transition-all"
      onClick={onClick}
    >
      {text}
    </button>
  );
}
