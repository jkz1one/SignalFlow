interface Props {
    time: string;
    x: number;
  }
  
  export default function CrosshairTooltip({ time, x }: Props) {
    return (
      <div
        className="absolute top-0 transform -translate-y-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded z-20 pointer-events-none"
        style={{
          left: `${x}px`,
          transform: 'translateX(-50%) translateY(-50%)',
        }}
      >
        {time}
      </div>
    );
  }
  