import os
from typing import List, Dict, Any

try:
    import pypdf
except ImportError:
    pypdf = None

class DocumentExtractor:
    def extract(self, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a document dictionary (from loader) and extracts text.
        Returns the same dictionary with an added 'pages' list:
        [{'page_number': 1, 'text': '...', 'section': None}, ...]
        """
        file_path = document_info["file_path"]
        file_type = document_info["file_type"]
        document_id = document_info["source_id"]

        pages = []
        if file_type == ".txt":
            pages = self._extract_txt(file_path)
        elif file_type == ".pdf":
            if not pypdf:
                raise ImportError("pypdf is required for PDF extraction.")
            pages = self._extract_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Basic structure detection can be applied here or downstream.
        # For now, sections are None unless detected.
        for page in pages:
            if "section" not in page:
                page["section"] = None

        document_info["pages"] = pages
        return document_info

    def _extract_txt(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split by double newline as a pseudo-page/paragraph heuristic for txt
        chunks = content.split("\n\n")
        pages = []
        for i, chunk in enumerate(chunks, 1):
            if chunk.strip():
                pages.append({"page_number": i, "text": chunk.strip()})
        return pages

    def _extract_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for i, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({"page_number": i, "text": text.strip()})
        except Exception as e:
            raise RuntimeError(f"PDF extraction failed: {str(e)}")
        return pages
