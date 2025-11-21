"use client";

import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ChatSession } from "@/types/chat";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, Trash2, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import UploadButton from "./UploadButton";
import UploadModal from "./UploadModal";
import KnowledgeList, { KnowledgeListRef } from "./KnowledgeList";
import { Separator } from "@/components/ui/separator";
import { useRef, useState } from "react";

interface Props {
  currentSessionId: string | null;
}

export default function ChatSidebar({ currentSessionId }: Props) {
  const router = useRouter();

  const [openUpload, setOpenUpload] = useState(false);
  const knowledgeRef = useRef<KnowledgeListRef>(null);

  const {
    data: sessions,
    refetch,
    isLoading,
  } = useQuery<ChatSession[]>({
    queryKey: ["sessions"],
    queryFn: async () => {
      const res = await api.get("/chat/sessions");
      return res.data;
    },
  });

  const handleNewChat = () => {
    router.push("/");
  };

  const handleOpenSession = (id: string) => {
    router.push(`/c/${id}`);
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await api.delete(`/chat/${id}`);
      refetch();
      if (currentSessionId === id) {
        router.push("/");
      }
    } catch (e) {
      console.error(e);
      alert("Gagal menghapus session");
    }
  };

  return (
    <>
      <div className="flex h-full flex-col">
        <div className="p-3 border-b space-y-2">
          <Button
            variant="default"
            size="sm"
            className="w-full justify-start gap-2"
            onClick={handleNewChat}
          >
            <Plus className="w-4 h-4" />
            New chat
          </Button>

          <UploadButton onClick={() => setOpenUpload(true)} />
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {isLoading && (
              <p className="text-xs text-neutral-500 px-2">
                Loading sessions...
              </p>
            )}
            {!isLoading && (!sessions || sessions.length === 0) && (
              <p className="text-xs text-neutral-400 px-2">No sessions yet</p>
            )}

            {sessions?.map((s) => (
              <div
                key={s.id}
                className={cn(
                  "group flex items-center justify-between rounded-md px-2 py-1.5 text-sm cursor-pointer hover:bg-neutral-200",
                  currentSessionId === s.id && "bg-neutral-200"
                )}
              >
                <button
                  className="flex items-center gap-2 flex-1 text-left"
                  onClick={() => handleOpenSession(s.id)}
                >
                  <MessageSquare className="w-4 h-4 text-neutral-500" />
                  <span className="truncate">{s.title || "New chat"}</span>
                </button>
                <button
                  className="opacity-0 group-hover:opacity-100 text-neutral-400 hover:text-red-500"
                  onClick={() => handleDeleteSession(s.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </ScrollArea>

        <Separator className="my-3" />

        <p className="px-3 text-xs font-medium text-neutral-500 mb-1">
          Knowledge
        </p>

        <KnowledgeList ref={knowledgeRef} />

        <div className="p-3 border-t text-[11px] text-neutral-400">
          Chat Knowledge Agent
          <br />
          UI mirip ChatGPT (light mode)
        </div>
      </div>

      {openUpload && (
        <UploadModal
          key="upload-modal"
          open={openUpload}
          onClose={() => setOpenUpload(false)}
          onUploaded={() => knowledgeRef.current?.refresh()}
        />
      )}
    </>
  );
}
