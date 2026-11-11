import React from 'react';

interface UserBubbleProps {
  text: string;
  timestamp?: string;
}

export const UserBubble: React.FC<UserBubbleProps> = ({ text, timestamp }) => {
  return (
    <div className="flex flex-col items-end self-end max-w-[85%] my-1">
      <div className="bg-[#126B73] text-white px-4 py-2.5 rounded-2xl rounded-br-sm shadow-xs leading-relaxed text-sm">
        <p className="whitespace-pre-line">{text}</p>
      </div>
      {timestamp && (
        <span className="text-[10px] text-[#596B72] mt-1 mr-1 font-medium">
          {timestamp}
        </span>
      )}
    </div>
  );
};
