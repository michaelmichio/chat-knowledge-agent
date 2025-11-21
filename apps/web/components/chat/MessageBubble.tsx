"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

interface Props {
  role: "user" | "assistant";
  content: string;
}

export function MessageBubble({ role, content }: Props) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <Avatar className="w-7 h-7">
          <AvatarFallback>AI</AvatarFallback>
        </Avatar>
      )}

      <div
        className={cn(
          "rounded-2xl px-3 py-2 text-sm max-w-[80%] whitespace-pre-wrap",
          isUser
            ? "bg-black text-white rounded-br-sm"
            : "bg-neutral-100 text-neutral-900 rounded-bl-sm"
        )}
      >
        {content}
      </div>

      {isUser && (
        <Avatar className="w-7 h-7">
          <AvatarFallback>U</AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}

export function TypingBubble() {
  return (
    <div className="flex gap-3 mb-4">
      <Avatar className="w-7 h-7">
        <AvatarFallback>AI</AvatarFallback>
      </Avatar>
      <div className="rounded-2xl px-3 py-2 text-sm max-w-[60%] bg-neutral-100 text-neutral-900 rounded-bl-sm">
        <span className="inline-flex gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-neutral-500 animate-bounce" />
          <span className="w-1.5 h-1.5 rounded-full bg-neutral-500 animate-bounce [animation-delay:0.15s]" />
          <span className="w-1.5 h-1.5 rounded-full bg-neutral-500 animate-bounce [animation-delay:0.3s]" />
        </span>
      </div>
    </div>
  );
}
