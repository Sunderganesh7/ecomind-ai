import re

class TextCleaner:
    def clean(self, text: str) -> str:
        """
        Conservatively cleans text.
        Removes repeated whitespace and unnecessary line breaks.
        Preserves scientific terminology, numbers, units, and qualifiers.
        """
        if not text:
            return ""
            
        # Replace multiple spaces with a single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Replace multiple newlines with a single newline to preserve paragraph boundaries
        # Wait, if extraction broke paragraphs with single newlines, we can heal them if they don't end in punctuation.
        # But for conservative cleaning, let's just normalize multi-newlines to double newlines (paragraphs)
        # and single newlines to spaces if they break a sentence.
        
        # 1. Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 2. Heal broken paragraphs: if a line doesn't end with punctuation and the next line starts with a lowercase letter,
        # it's likely a wrapped line. We can do a simpler heuristic:
        # Just replace single newlines with a space, but keep double newlines.
        # This is safe for most PDFs.
        paragraphs = text.split('\n\n')
        cleaned_paragraphs = []
        
        for para in paragraphs:
            # Replace single newlines within a paragraph with a space
            para = para.replace('\n', ' ')
            # Clean up resulting multiple spaces again
            para = re.sub(r' +', ' ', para).strip()
            if para:
                cleaned_paragraphs.append(para)
                
        return '\n\n'.join(cleaned_paragraphs)

    def clean_document(self, document: dict) -> dict:
        for page in document.get("pages", []):
            page["text"] = self.clean(page["text"])
        return document
