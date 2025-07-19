export default function SmallButtons({ back, next }) {
  const button = [
    {
      name: "back",
      icon: (
        <svg
          width="76"
          height="16"
          viewBox="0 0 76 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M0.792892 8.70711C0.402367 8.31658 0.402367 7.68342 0.792892 7.29289L7.15685 0.928932C7.54738 0.538408 8.18054 0.538408 8.57107 0.928932C8.96159 1.31946 8.96159 1.95262 8.57107 2.34315L2.91422 8L8.57107 13.6569C8.96159 14.0474 8.96159 14.6805 8.57107 15.0711C8.18054 15.4616 7.54738 15.4616 7.15685 15.0711L0.792892 8.70711ZM75.5 8V9H1.5V8V7H75.5V8Z"
            fill="white"
          />
        </svg>
      ),
    },
    {
      name: "next",
      icon: (
        <svg
          width="76"
          height="16"
          viewBox="0 0 76 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M75.2071 8.70711C75.5976 8.31658 75.5976 7.68342 75.2071 7.29289L68.8431 0.928932C68.4526 0.538408 67.8195 0.538408 67.4289 0.928932C67.0384 1.31946 67.0384 1.95262 67.4289 2.34315L73.0858 8L67.4289 13.6569C67.0384 14.0474 67.0384 14.6805 67.4289 15.0711C67.8195 15.4616 68.4526 15.4616 68.8431 15.0711L75.2071 8.70711ZM0.5 8V9H74.5V8V7H0.5V8Z"
            fill="white"
          />
        </svg>
      ),
    },
  ];

  return (
    <div className="flex flex-col gap-y-2 items-center">
      <div className="flex gap-x-2">
        {button.map((item) => (
          <button
            key={item.name}
            onClick={item.name === "back" ? back : next}
            className="bg-[#002448] w-[149px] h-[59px] text-white flex items-center justify-center rounded-full"
          >
            {item.icon}
          </button>
        ))}
      </div>
    </div>
  );
}
