"use client";

import { useParams } from "next/navigation";
import { useEffect } from "react";
import { useChatStore } from "@/store/chatStore";
import ChatLayout from "@/components/chat/ChatLayout";

export default function ChatSessionPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const setCurrentSessionId = useChatStore((s) =>
    s.currentSessionId === sessionId
      ? s.setCurrentSessionId
      : s.setCurrentSessionId
  );

  useEffect(() => {
    setCurrentSessionId(sessionId);
  }, [sessionId, setCurrentSessionId]);

  return <ChatLayout sessionId={sessionId} />;
}
