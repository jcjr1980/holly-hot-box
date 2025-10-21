import os
import json
import logging
from typing import Dict, List, Optional
from .llm_orchestrator import LLMOrchestrator

logger = logging.getLogger(__name__)

class FileSummarizer:
    """Intelligent file summarization with LLM recommendations"""
    
    def __init__(self):
        self.orchestrator = LLMOrchestrator()
        
    def recommend_llm(self, content_type: str) -> Dict:
        """Recommend best LLM based on content type"""
        recommendations = {
            'contract': {
                'primary': 'claude',
                'reason': 'Claude excels at legal document analysis and contract review',
                'secondary': 'gemini'
            },
            'chat_history': {
                'primary': 'gemini',
                'reason': 'Gemini Tier 3 best at conversation summarization and context retention',
                'secondary': 'deepseek'
            },
            'email': {
                'primary': 'gemini',
                'reason': 'Gemini Tier 3 excellent at email content analysis and summarization',
                'secondary': 'claude'
            },
            'business_email': {
                'primary': 'gemini',
                'reason': 'Gemini Tier 3 best for business email analysis and action item extraction',
                'secondary': 'claude'
            },
            'customer_support': {
                'primary': 'claude',
                'reason': 'Claude excellent at understanding customer issues and support context',
                'secondary': 'gemini'
            },
            'meeting_notes': {
                'primary': 'gemini',
                'reason': 'Gemini Tier 3 best at extracting key points and action items from meetings',
                'secondary': 'claude'
            },
            'proposal': {
                'primary': 'gemini',
                'reason': 'Gemini Tier 3 excellent at analyzing proposals and business pitches',
                'secondary': 'claude'
            },
            'financial': {
                'primary': 'claude',
                'reason': 'Claude best at financial document analysis and data extraction',
                'secondary': 'gemini'
            },
            'technical': {
                'primary': 'deepseek',
                'reason': 'DeepSeek superior for technical content and code analysis',
                'secondary': 'gemini'
            },
            'business': {
                'primary': 'gemini',
                'reason': 'Gemini Tier 3 excellent at business document analysis',
                'secondary': 'claude'
            },
            'research': {
                'primary': 'gemini',
                'reason': 'Gemini Tier 3 handles research papers and academic content well',
                'secondary': 'claude'
            },
            'general': {
                'primary': 'gemini',
                'reason': 'Gemini Tier 3 best all-around summarizer',
                'secondary': 'claude'
            }
        }
        return recommendations.get(content_type, recommendations['general'])
    
    def summarize_file(self, content: str, content_type: str, llm: Optional[str] = None) -> Dict:
        """Summarize file with recommended or specified LLM"""
        if not llm:
            recommendation = self.recommend_llm(content_type)
            llm = recommendation['primary']
        
        # Build specialized prompt based on content type
        prompts = {
            'contract': """Analyze this contract and extract:
- Parties involved
- Key terms and conditions  
- Financial obligations
- Important dates and deadlines
- Potential issues or red flags
- Breach conditions""",
            
            'chat_history': """Summarize this conversation:
- Main topics discussed
- Key decisions made
- Action items identified
- Important insights
- Unresolved questions""",
            
            'email': """Analyze this email and extract:
- Main subject and purpose
- Key points and information
- Action items or requests
- Important dates or deadlines
- Follow-up needed""",
            
            'business_email': """Analyze this business email and extract:
- Business context and purpose
- Key decisions or agreements
- Action items and responsibilities
- Timeline and deadlines
- Stakeholders involved""",
            
            'customer_support': """Analyze this customer support communication and extract:
- Customer issue or request
- Resolution steps taken
- Status and next actions
- Escalation points
- Customer satisfaction indicators""",
            
            'meeting_notes': """Analyze these meeting notes and extract:
- Main topics discussed
- Key decisions made
- Action items with owners
- Important deadlines
- Next steps and follow-ups""",
            
            'proposal': """Analyze this proposal and extract:
- Main proposal objectives
- Key features or benefits
- Timeline and milestones
- Budget or cost information
- Success metrics""",
            
            'financial': """Analyze this financial document and extract:
- Financial metrics and data
- Key financial insights
- Trends and patterns
- Important numbers and calculations
- Financial recommendations""",
            
            'technical': """Analyze this technical content:
- Main concepts
- Technical specifications
- Implementation details
- Key findings or conclusions""",
            
            'business': """Summarize this business document:
- Key objectives
- Strategic points
- Financial information
- Action items
- Stakeholders mentioned""",
            
            'research': """Summarize this research content:
- Main hypothesis/question
- Methodology
- Key findings
- Conclusions
- Implications""",
            
            'general': """Create a comprehensive summary:
- Main points
- Key information
- Important details
- Conclusions or takeaways"""
        }
        
        prompt = prompts.get(content_type, prompts['general'])
        full_prompt = f"{prompt}\n\nDocument content:\n{content}"
        
        try:
            # Use orchestrator to get response from recommended LLM
            if llm == 'gemini':
                response, metadata = self.orchestrator.query_gemini(full_prompt)
            elif llm == 'claude':
                response, metadata = self.orchestrator.query_claude(full_prompt)
            elif llm == 'deepseek':
                response, metadata = self.orchestrator.query_deepseek(full_prompt)
            else:
                # Default to Gemini
                response, metadata = self.orchestrator.query_gemini(full_prompt)
                llm = 'gemini'
            
            return {
                'summary': response,
                'llm_used': llm,
                'metadata': metadata,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return {
                'summary': f"Error summarizing file: {str(e)}",
                'llm_used': llm,
                'metadata': {},
                'success': False
            }
    
    def process_file_content(self, file_path: str, file_type: str) -> str:
        """Extract text content from various file types"""
        try:
            if file_type in ['text/plain', 'text/markdown']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_type == 'application/json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            
            elif file_type in ['message/rfc822', 'application/vnd.ms-outlook']:  # .eml, .msg files
                # TODO: Add email parsing with email library
                return "[Email content extraction coming soon]"
            
            elif file_type == 'application/pdf':
                # TODO: Add PDF extraction with PyPDF2
                return "[PDF content extraction coming soon]"
            
            elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                # TODO: Add DOCX extraction with python-docx
                return "[DOCX content extraction coming soon]"
            
            else:
                return f"[File type {file_type} not yet supported for text extraction]"
                
        except Exception as e:
            logger.error(f"File processing error: {e}")
            return f"Error processing file: {str(e)}"
    
    def should_summarize(self, content: str, file_size: int) -> bool:
        """Determine if file should be summarized"""
        # Summarize if > 10KB or content > 5000 characters
        return file_size > 10240 or len(content) > 5000
    
    def summarize_large_file(self, content: str, content_type: str, max_chunk_size: int = 50000) -> Dict:
        """Split large files and summarize in chunks"""
        try:
            # Split content into chunks
            chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]
            
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                chunk_prompt = f"Summarize this chunk {i+1} of {len(chunks)}:\n\n{chunk}"
                response, _ = self.orchestrator.query_gemini(chunk_prompt)
                chunk_summaries.append(f"Chunk {i+1}: {response}")
            
            # Combine chunk summaries into master summary
            combined_content = "\n\n".join(chunk_summaries)
            master_prompt = f"Create a comprehensive summary from these chunk summaries:\n\n{combined_content}"
            
            final_response, metadata = self.orchestrator.query_gemini(master_prompt)
            
            return {
                'summary': final_response,
                'llm_used': 'gemini',
                'metadata': metadata,
                'success': True,
                'chunk_count': len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Large file summarization error: {e}")
            return {
                'summary': f"Error summarizing large file: {str(e)}",
                'llm_used': 'gemini',
                'metadata': {},
                'success': False
            }
