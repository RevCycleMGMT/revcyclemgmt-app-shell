"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { ClaimFormData } from "@/lib/claims/form-data";

interface GeneratePdfButtonProps {
  formData: ClaimFormData;
}

function pdfFilename(formData: ClaimFormData) {
  const safeLastName = formData.patient.lastName.replace(/[^A-Za-z0-9]/g, "");
  return `CMS-1500_${safeLastName}_${formData.encounter.dateOfService}.pdf`;
}

export function GeneratePdfButton({ formData }: GeneratePdfButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const generatePdf = async () => {
    setIsGenerating(true);

    try {
      const [{ pdf }, { Cms1500PdfDocument }] = await Promise.all([
        import("@react-pdf/renderer"),
        import("@/components/pipeline/Cms1500PdfDocument"),
      ]);
      const blob = await pdf(
        <Cms1500PdfDocument formData={formData} />
      ).toBlob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");

      anchor.href = url;
      anchor.download = pdfFilename(formData);
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Button
      type="button"
      variant="outline"
      className="rounded-lg border-teal-200 text-teal-700 hover:bg-teal-50 hover:text-teal-800"
      onClick={generatePdf}
      disabled={isGenerating}
    >
      {isGenerating ? (
        <Loader2 className="size-4 animate-spin" aria-hidden="true" />
      ) : (
        <Download className="size-4" aria-hidden="true" />
      )}
      {isGenerating ? "Generating" : "Generate PDF"}
    </Button>
  );
}
