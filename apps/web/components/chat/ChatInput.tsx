"use client";

import { useState, KeyboardEvent } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";

interface Props {
  onSend: (text: string) => Promise<void> | void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");

  const handleSend = async () => {
    const text = value.trim();
    if (!text) return;
    setValue("");
    await onSend(text);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!disabled) {
        handleSend();
      }
    }
  };

  return (
    <div className="border-t bg-white">
      <div className="max-w-3xl mx-auto px-3 py-3 flex items-end gap-2">
        <Textarea
          rows={1}
          value={value}
          disabled={disabled}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          className="min-h-[44px] max-h-40 resize-none text-sm bg-neutral-50"
          placeholder="Message Chat Agent..."
        />
        <Button
          size="icon"
          disabled={disabled || !value.trim()}
          onClick={handleSend}
          className="shrink-0"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
