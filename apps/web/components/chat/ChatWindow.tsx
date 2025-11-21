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
  const [isSending, setIsSending] = useState(false);

  const {
    data: messages,
    isLoading,
    refetch,
  } = useQuery<ChatMessage[]>({
    queryKey: ["messages", sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const res = await api.get(`/chat/${sessionId}/messages`);
      return res.data;
    },
    enabled: !!sessionId,
  });

  useEffect(() => {
    // scroll to bottom after messages load
    const el = document.getElementById("chat-scroll-anchor");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }, [messages?.length]);

  const handleSend = async (text: string) => {
    try {
      setIsSending(true);

      // CASE 1: Belum ada session → buat dulu, lalu kirim, lalu redirect
      if (!sessionId) {
        const startRes = await api.post("/chat/start");
        const newId = startRes.data.id;

        await api.post("/chat/send", null, {
          params: { session_id: newId, message: text },
        });

        router.push(`/c/${newId}`);
        return;
      }

      // CASE 2: sudah ada session → kirim langsung
      await api.post("/chat/send", null, {
        params: { session_id: sessionId, message: text },
      });

      await refetch();
    } catch (e) {
      console.error(e);
      alert("Gagal mengirim pesan");
    } finally {
      setIsSending(false);
    }
  };

  const hasMessages = (messages?.length || 0) > 0;

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="border-b px-4 py-2 text-sm text-neutral-500 flex items-center justify-between">
        <span>Chat Knowledge Agent</span>
      </div>

      <ScrollArea className="flex-1">
        <div className="max-w-3xl mx-auto px-4 py-6">
          {!hasMessages && !isLoading && (
            <div className="text-center text-neutral-400 text-sm mt-20 space-y-2">
              <p className="text-lg font-medium text-neutral-800">
                How can I help you today?
              </p>
              <p>
                Mulai dengan mengetik pertanyaan di bawah seperti di ChatGPT.
              </p>
            </div>
          )}

          {messages?.map((m) => (
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
