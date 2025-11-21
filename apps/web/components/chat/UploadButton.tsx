"use client";

import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function UploadButton({ onClick }: { onClick: () => void }) {
  return (
    <Button
      variant="outline"
      size="sm"
      className="w-full justify-start gap-2"
      onClick={onClick}
    >
      <Upload className="w-4 h-4" />
      Upload Knowledge
    </Button>
  );
}
