"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import KnowledgeItem from "./KnowledgeItem";
import { forwardRef, useImperativeHandle } from "react";

export interface KnowledgeListRef {
  refresh: () => void;
}

const KnowledgeList = forwardRef<KnowledgeListRef>((props, ref) => {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["knowledge"],
    queryFn: async () => {
      const res = await api.get("/docs/inspect");
      return res.data;
    },
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: false,
  });

  // ➤ expose refresh() ke parent
  useImperativeHandle(ref, () => ({
    refresh() {
      refetch();
    },
  }));

  if (isLoading) return <p className="text-xs p-3">Loading knowledge...</p>;

  return (
    <ScrollArea className="h-full">
      <div className="p-2 space-y-2">
        {data?.metadata?.map((doc: any) => (
          <KnowledgeItem key={doc.id} doc={doc} onDeleted={refetch} />
        ))}
      </div>
    </ScrollArea>
  );
});

export default KnowledgeList;
