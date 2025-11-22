"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ChatMessage } from "@/types/chat";
import ChatInput from "./ChatInput";
import { MessageBubble, TypingBubble } from "./MessageBubble";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

interface Props {
  sessionId: string | null;
}

export default function ChatWindow({ sessionId }: Props) {
  const router = useRouter();

  const [localMessages, setLocalMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  // Fetch pesan dari backend
  const { data: messages } = useQuery<ChatMessage[]>({
    queryKey: ["messages", sessionId],
    queryFn: async () => {
      if (!sessionId) {
        return []};
      const res = await api.get(`/chat/${sessionId}/messages`);
      return res.data;
    },
    enabled: !!sessionId,
    refetchOnWindowFocus: false, // ⛔ JANGAN fetch ketika window fokus
    refetchOnMount: false, // ⛔ JANGAN fetch ketika component mount
    refetchOnReconnect: false, // ⛔ JANGAN fetch ketika internet kembali
    retry: false,
  });

  useEffect(() => {
    if (!sessionId) setLocalMessages([]);
  }, [sessionId]);

  // Sinkronisasi messages backend ke localMessages
  useEffect(() => {
    if (messages) setLocalMessages(messages);
  }, [messages]);

  // Scroll otomatis
  useEffect(() => {
    const el = document.getElementById("chat-scroll-anchor");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }, [localMessages.length, isSending]);

  // =============================
  //           HANDLE SEND
  // =============================
  const handleSend = async (text: string) => {
    try {
      setIsSending(true);

      // optimistic user message
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
      };
      setLocalMessages((prev) => [...prev, userMessage]);

      // CASE 1: create new session
      if (!sessionId) {
        const start = await api.post("/chat/start");
        const newId = start.data.id;

        // send message
        await api.post("/chat/send", null, {
          params: { session_id: newId, message: text },
        });

        // redirect → page only fetches once
        router.push(`/c/${newId}`);

        return;
      }

      // CASE 2: existing session
      const res = await api.post("/chat/send", null, {
        params: { session_id: sessionId, message: text },
      });

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.data.answer,
      };

      setLocalMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      alert("Gagal mengirim pesan");
    } finally {
      setIsSending(false);
    }
  };

  const hasMessages = localMessages.length > 0;

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="border-b px-4 py-2 text-sm text-neutral-500 flex items-center justify-between">
        <span>Chat Knowledge Agent</span>
      </div>

      <ScrollArea className="flex-1 overflow-auto">
        <div className="max-w-3xl mx-auto px-4 py-6">
          {!hasMessages && (
            <div className="text-center text-neutral-400 text-sm mt-20 space-y-2">
              <p className="text-lg font-medium text-neutral-800">
                How can I help you today?
              </p>
              <p>
                Mulai dengan mengetik pertanyaan di bawah seperti di ChatGPT.
              </p>
            </div>
          )}

          {localMessages
            .filter((m) => m && m.role && m.content)
            .map((m) => (
              <MessageBubble key={m.id} role={m.role} content={m.content} />
            ))}

          {isSending && <TypingBubble />}

          <div id="chat-scroll-anchor" />
        </div>
      </ScrollArea>

      <Separator />
      <ChatInput onSend={handleSend} disabled={isSending} />
    </div>
  );
}
