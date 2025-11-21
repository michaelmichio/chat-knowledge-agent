"use client";

import { useParams } from "next/navigation";
import ChatSidebar from "./ChatSidebar";
import ChatWindow from "./ChatWindow";

export default function ChatLayout() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  return (
    <div className="flex h-screen">
      <div className="hidden md:flex md:w-72 border-r bg-neutral-50">
        <ChatSidebar currentSessionId={sessionId} />
      </div>
      <div className="flex-1 flex flex-col">
        <ChatWindow sessionId={sessionId} />
      </div>
    </div>
  );
}
