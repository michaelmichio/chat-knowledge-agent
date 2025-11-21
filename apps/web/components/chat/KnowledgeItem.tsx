"use client";

import { Trash2, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

export default function KnowledgeItem({
  doc,
  onDeleted,
}: {
  doc: any;
  onDeleted: () => void;
}) {
  const remove = async () => {
    if (!confirm("Delete this document?")) return;

    await api.delete(`/docs/${doc.id}`);
    onDeleted();
  };

  return (
    <div className="flex items-center justify-between p-2 rounded hover:bg-neutral-200">
      <div className="flex items-center gap-2">
        <FileText className="w-4 h-4 text-neutral-600" />
        <span className="text-sm">{doc.filename}</span>
      </div>

      <Button variant="ghost" size="icon" onClick={remove}>
        <Trash2 className="w-4 h-4 text-red-500" />
      </Button>
    </div>
  );
}
