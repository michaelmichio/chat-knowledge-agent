"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export default function UploadModal({
  open,
  onClose,
  onUploaded,
}: {
  open: boolean;
  onClose: () => void;
  onUploaded: () => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const upload = async () => {
    if (!file) return;
    setLoading(true);

    const form = new FormData();
    form.append("file", file);

    try {
      await api.post("/docs/process", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      onUploaded();
      onClose();
      setFile(null);
    } catch (e) {
      console.error(e);
      alert("Upload gagal");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/10 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow p-6 w-[360px]">
        <h2 className="text-lg font-semibold mb-4">Upload Knowledge</h2>

        <input
          type="file"
          className="mb-4 border-dashed border-2 border-black p-2 rounded-xl bg-neutral-200"
          onChange={(e) => {
            const f = e.target.files?.[0] || null;
            setFile(f);
          }}
        />

        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={upload} disabled={!file || loading}>
            {loading ? "Uploading..." : "Upload"}
          </Button>
        </div>
      </div>
    </div>
  );
}
