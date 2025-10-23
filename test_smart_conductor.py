#!/usr/bin/env python3
"""
Test the SmartConductor with Johnny's actual Cellpay lawsuit query
This runs LOCALLY to verify everything works before deploying
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# Mock Django settings for standalone testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hbb_core.settings')

# Import after Django setup
from brain_chat.llm_orchestrator import LLMOrchestrator
from brain_chat.smart_conductor import SmartConductor


class MockProject:
    """Mock project object for testing"""
    def __init__(self):
        self.name = "Johnny Collins vs Cellpay/Parvez Jasani"
        self.description = """Legal case against Cellpay and Parvez Jasani for breach of contract, 
fraud, and unpaid commissions. Dispute over payment processing services and contractual obligations."""
        
        self.summary = """CASE SUMMARY:
- Contract dispute with Cellpay regarding payment processing services
- Allegations of breach of contract and fraud by Parvez Jasani
- Significant unpaid commissions owed
- Multiple contract violations and misrepresentations
- Potential damages in excess of $100,000
- Strong documentation including contracts, emails, and transaction records
- Case suitable for contingency representation due to clear liability and substantial damages"""
        
        self.files = MockFileManager()


class MockFile:
    """Mock file object"""
    def __init__(self, name, summary):
        self.file_name = name
        self.summary = summary
        self.original_content = ""


class MockFileManager:
    """Mock file manager"""
    def all(self):
        return [
            MockFile("Cellpay_Contract.pdf", "Original contract showing payment terms and commission structure"),
            MockFile("Email_Thread_Jan_2024.txt", "Email communications showing promises and subsequent breach"),
            MockFile("Transaction_Records.xlsx", "Financial records showing unpaid amounts"),
            MockFile("Communication_Log.pdf", "Timeline of attempts to resolve dispute"),
        ]
    
    def exists(self):
        return True


def test_smart_conductor():
    """Test the SmartConductor with the actual Cellpay query"""
    
    print("=" * 80)
    print("🧪 TESTING SMART CONDUCTOR WITH CELLPAY LAWSUIT QUERY")
    print("=" * 80)
    
    # The actual query from Johnny
    query = """Hello Holly! Based on my uploaded case files and summary, analyze my legal situation and identify the specific areas of law that apply to my case. What type of legal expertise should I prioritize when searching for a Miami-Dade law firm? Can you help me by finding Miami-Dade law firms specializing in business/contract litigation that work on contingency. Based on my case details, what makes it attractive to contingency lawyers? Please analyze my case files and identify the strongest legal arguments and potential damages. What aspects make this case attractive to contingency lawyers. Review my case files and create a comprehensive legal strategy summary. Include: 1) Key legal issues, 2) Potential damages, 3) Case strengths, 4) Recommended legal expertise needed. Then create a spreadsheet template for tracking law firms, their specialties, contact information, and my notes from consultations. Based on my consultation notes, which firms seem most suitable for my case? What additional questions should I ask?"""
    
    print(f"\n📝 Query length: {len(query)} characters")
    print(f"📝 Query words: {len(query.split())} words")
    
    # Create mock project
    mock_project = MockProject()
    print(f"\n📁 Project: {mock_project.name}")
    print(f"📁 Description: {mock_project.description[:100]}...")
    print(f"📁 Summary length: {len(mock_project.summary)} chars")
    print(f"📁 Files: {len(mock_project.files.all())}")
    
    # Initialize orchestrator and conductor
    print("\n🔧 Initializing LLM Orchestrator...")
    orchestrator = LLMOrchestrator()
    
    print("🎭 Initializing SmartConductor...")
    conductor = SmartConductor(orchestrator, project=mock_project)
    
    # Test the conductor
    print("\n🚀 Executing query...")
    print("-" * 80)
    
    try:
        result = conductor.conduct_query(query, conversation_history=[])
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS! SmartConductor completed")
        print("=" * 80)
        
        print(f"\n📊 Mode: {result.get('mode')}")
        print(f"📊 Conductor used: {result.get('conductor_used', False)}")
        
        if result.get('sub_questions_count'):
            print(f"📊 Sub-questions: {result.get('sub_questions_count')}")
            print(f"📊 Successful answers: {result.get('successful_answers')}")
        
        if result.get('metadata'):
            metadata = result['metadata']
            if isinstance(metadata, dict):
                print(f"📊 Tokens: {metadata.get('total_tokens', 'N/A')}")
                print(f"📊 Response time: {metadata.get('total_response_time_ms', 'N/A')}ms")
        
        response_text = result.get('response', result.get('final_response', ''))
        print(f"\n📄 Response length: {len(response_text)} characters")
        print(f"\n📄 Response preview (first 500 chars):\n")
        print(response_text[:500])
        print("\n... (response continues) ...")
        
        print("\n" + "=" * 80)
        print("✅ TEST PASSED - SmartConductor is working!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"\n💥 Error: {type(e).__name__}: {str(e)}")
        
        import traceback
        print(f"\n📋 Traceback:")
        traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("❌ SmartConductor needs fixes before deployment")
        print("=" * 80)
        
        return False


if __name__ == "__main__":
    print("\n🔬 Starting SmartConductor Test Suite\n")
    
    # Check API keys
    print("🔑 Checking API keys...")
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"   Gemini API key: {'✅ Found' if gemini_key else '❌ Missing'}")
    
    if not gemini_key:
        print("\n❌ ERROR: GEMINI_API_KEY not found in environment")
        print("   Make sure .env file exists and contains GEMINI_API_KEY")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    
    # Run the test
    success = test_smart_conductor()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ READY TO DEPLOY - All tests passed!")
    else:
        print("❌ NOT READY - Fix errors before deploying")
    print("=" * 80 + "\n")
    
    sys.exit(0 if success else 1)

