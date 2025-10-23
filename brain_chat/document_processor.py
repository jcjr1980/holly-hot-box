"""
Document Processing Pipeline for Holly Hot Box
Processes uploaded files, extracts text, generates summaries
"""
import logging
import os
from typing import Dict, List
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Handles document processing for legal case files
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def process_file(self, project_file) -> Dict:
        """
        Process a single uploaded file:
        1. Extract text content
        2. Generate AI summary
        3. Categorize document type
        4. Store metadata
        """
        logger.info(f"📄 Processing file: {project_file.file_name}")
        
        try:
            # Step 1: Extract text based on file type
            text_content = self._extract_text(project_file)
            
            if not text_content:
                logger.warning(f"No text extracted from {project_file.file_name}")
                return {
                    "success": False,
                    "error": "Could not extract text from file"
                }
            
            logger.info(f"✅ Extracted {len(text_content)} chars from {project_file.file_name}")
            
            # Step 2: Generate AI summary
            summary = self._generate_summary(text_content, project_file.file_name)
            
            # Step 3: Categorize document
            category = self._categorize_document(text_content, project_file.file_name)
            
            # Step 4: Store in database
            project_file.original_content = text_content[:10000]  # Store first 10k chars
            project_file.summary = summary
            project_file.content_type = category
            project_file.is_summarized = True
            project_file.summarized_by = 'gemini'
            project_file.save()
            
            logger.info(f"✅ Processed {project_file.file_name}: {category} ({len(summary)} char summary)")
            
            return {
                "success": True,
                "summary": summary,
                "category": category,
                "text_length": len(text_content)
            }
            
        except Exception as e:
            logger.error(f"Failed to process {project_file.file_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_text(self, project_file) -> str:
        """Extract text from various file types"""
        file_type = project_file.file_type.lower()
        
        try:
            # Read file content
            file_path = project_file.file_path.path
            
            if file_type in ['txt', 'text']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            elif file_type == 'pdf':
                # For now, return placeholder - would need PyPDF2 or similar
                return f"[PDF content from {project_file.file_name} - PDF extraction requires additional library]"
            
            elif file_type in ['doc', 'docx']:
                # Would need python-docx
                return f"[DOCX content from {project_file.file_name} - DOCX extraction requires additional library]"
            
            elif file_type == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            
            else:
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Text extraction failed for {project_file.file_name}: {e}")
            return ""
    
    def _generate_summary(self, text: str, filename: str) -> str:
        """Generate AI summary of document"""
        # Truncate if too long (Gemini can handle ~30k chars, but keep it reasonable)
        text_to_summarize = text[:8000] if len(text) > 8000 else text
        
        summary_prompt = f"""You are analyzing a legal document. Provide a concise 150-word summary that captures:
1. Document type (contract, email, transaction record, etc.)
2. Key parties involved
3. Main points or obligations
4. Relevant dates or amounts
5. Legal significance

Document: {filename}

Content:
{text_to_summarize}

Provide ONLY the summary, no preamble."""
        
        try:
            summary, _ = self.orchestrator.query_gemini(summary_prompt, [])
            return summary[:500]  # Cap at 500 chars
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Document: {filename} ({len(text)} characters)"
    
    def _categorize_document(self, text: str, filename: str) -> str:
        """Categorize document type using AI"""
        text_sample = text[:2000]  # Just first 2k chars for categorization
        
        categorization_prompt = f"""Categorize this legal document into ONE of these categories:
- contract
- email_correspondence
- transaction_record
- court_filing
- agreement
- invoice
- communication_log
- evidence
- general

Document: {filename}
Content sample: {text_sample}

Return ONLY the category name, nothing else."""
        
        try:
            category, _ = self.orchestrator.query_gemini(categorization_prompt, [])
            category = category.strip().lower()
            
            # Validate it's one of our categories
            valid_categories = ['contract', 'email_correspondence', 'transaction_record', 
                              'court_filing', 'agreement', 'invoice', 'communication_log', 
                              'evidence', 'general']
            
            if category in valid_categories:
                return category
            else:
                return 'general'
                
        except Exception as e:
            logger.error(f"Categorization failed: {e}")
            return 'general'
    
    def build_query_context(self, project, user_query: str) -> str:
        """
        Build intelligent context for a query by selecting relevant files
        """
        try:
            files = list(project.files.filter(is_summarized=True))
            
            if not files:
                return ""
            
            # For now, include ALL file summaries (they're concise)
            # In future, could use AI to select only relevant ones
            context_parts = []
            
            if project.summary:
                context_parts.append(f"CASE SUMMARY:\n{project.summary}\n")
            
            context_parts.append("CASE FILES:")
            for f in files:
                context_parts.append(f"\n📄 {f.file_name} ({f.content_type}):")
                context_parts.append(f"   {f.summary}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Context building failed: {e}")
            return ""

