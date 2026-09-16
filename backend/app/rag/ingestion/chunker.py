import textwrap
from typing import List, Dict, Any

class TextChunker:
    def __init__(self, chunk_size_words: int = 200, chunk_overlap_words: int = 50):
        # We use words as a proxy for tokens to avoid heavy dependencies (like tiktoken) 
        # unless strictly necessary. 200 words is approx 250-300 tokens.
        self.chunk_size = chunk_size_words
        self.chunk_overlap = chunk_overlap_words

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_index = 0
        
        for page in document.get("pages", []):
            page_num = page["page_number"]
            section = page.get("section")
            text = page["text"]
            
            paragraphs = text.split('\n\n')
            current_chunk_words = []
            
            for para in paragraphs:
                para_words = para.split()
                
                # If adding this paragraph exceeds chunk size significantly, save current chunk and start new
                if len(current_chunk_words) + len(para_words) > self.chunk_size and current_chunk_words:
                    chunks.append(self._create_chunk_obj(document, page_num, section, chunk_index, current_chunk_words))
                    chunk_index += 1
                    
                    # Keep overlap
                    current_chunk_words = current_chunk_words[-self.chunk_overlap:] if self.chunk_overlap > 0 else []
                
                current_chunk_words.extend(para_words)
                
                # If a single paragraph is still larger than chunk size, split it (rare, but possible)
                while len(current_chunk_words) > self.chunk_size:
                    chunks.append(self._create_chunk_obj(document, page_num, section, chunk_index, current_chunk_words[:self.chunk_size]))
                    chunk_index += 1
                    current_chunk_words = current_chunk_words[self.chunk_size - self.chunk_overlap:]
            
            # Flush remaining words in the page
            if current_chunk_words:
                chunks.append(self._create_chunk_obj(document, page_num, section, chunk_index, current_chunk_words))
                chunk_index += 1
                
        return chunks

    def _create_chunk_obj(self, document, page_num, section, chunk_index, words_list):
        text = " ".join(words_list)
        return {
            "document_id": document["source_id"],
            "page_number": page_num,
            "section": section,
            "chunk_index": chunk_index,
            "text": text
        }
