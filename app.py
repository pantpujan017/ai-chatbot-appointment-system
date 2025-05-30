# app.py
import streamlit as st
import os
from utils.document_processor import DocumentProcessor
from utils.form_handler import FormHandler
from utils.chatbot import ChatBot
from utils.date_extractor import DateExtractor

# Page configuration
st.set_page_config(
    page_title="ML Chatbot - Document Q&A & Appointment Booking",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
# Replace the existing CSS section in your app.py with this:

# Replace the existing CSS section in your app.py with this:

# Replace the existing CSS section in your app.py with this:

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B35;  /* Changed from #2E86AB - Orange/Red header */
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E8F5E8;  /* Changed from #E3F2FD - Light green for user */
        margin-left: 2rem;
        border-left: 4px solid #4CAF50;  /* Added green border */
        color: black;  /* Black text for user messages */
    }
    .bot-message {
        background-color: #FFF3E0;  /* Changed from #F5F5F5 - Light orange for bot */
        margin-right: 2rem;
        border-left: 4px solid #FF9800;  /* Added orange border */
        color: black;  /* Black text for bot messages */
    }
    .sidebar-section {
        background-color: #F3E5F5;  /* Changed from #F8F9FA - Light purple sidebar */
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    /* Additional styling options */
    .stApp {
        background-color: #FAFAFA;  /* Light gray app background */
        color: black;  /* Ensure all text is black */
    }
    
    /* Force all text elements to be black */
    .main .block-container {
        color: black;
    }
    
    /* Specifically target markdown and text elements */
    .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }
    
    /* Chat input text */
    .stChatInput input {
        color: black !important;
    }
    
    /* Customize button colors */
    .stButton > button {
        background-color: #673AB7;  /* Purple buttons */
        color: white;
        border: none;
        border-radius: 8px;
    }
    
    .stButton > button:hover {
        background-color: #5E35B1;  /* Darker purple on hover */
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'documents_processed' not in st.session_state:
        st.session_state.documents_processed = False
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = None
    if 'form_handler' not in st.session_state:
        st.session_state.form_handler = None

def setup_sidebar():
    """Setup the sidebar with configuration options"""
    with st.sidebar:
        st.markdown("## 🔧 Configuration")
        
        # API Key input
        st.markdown("### Google Gemini API Key")
        if 'api_key' not in st.session_state or not st.session_state.api_key:
            try:
                st.session_state.api_key = st.secrets["GEMINI_API_KEY"]
            except:
                st.session_state.api_key = "your-fallback-api-key"
        
        
        
        # Document upload section
        st.markdown("### 📄 Document Upload")
        uploaded_files = st.file_uploader(
            "Upload documents for Q&A:",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload PDF, DOCX, or TXT files"
        )
        
        if uploaded_files and st.session_state.api_key:
            if st.button("Process Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    try:
                        # Initialize document processor
                        doc_processor = DocumentProcessor(st.session_state.api_key)
                        
                        # Load and process documents
                        documents = doc_processor.load_documents(uploaded_files)
                        vector_store = doc_processor.create_vector_store(documents)
                        
                        if vector_store:
                            st.session_state.document_processor = doc_processor
                            st.session_state.documents_processed = True
                            st.session_state.chatbot = None  # Reset chatbot to include new documents
                            st.success(f"Successfully processed {len(uploaded_files)} documents!")
                        else:
                            st.error("Failed to process documents.")
                    except Exception as e:
                        st.error(f"Error processing documents: {str(e)}")
        
        # Features section
        st.markdown("### ✨ Features")
        st.markdown("""
        - **Document Q&A**: Ask questions about uploaded documents
        - **Appointment Booking**: Schedule calls with conversational forms
        - **Smart Date Parsing**: Understands "next Monday", "tomorrow", etc.
        - **Input Validation**: Email, phone, and date validation
        - **Conversation Memory**: Maintains context across messages
        """)
        
        # Status section
        st.markdown("### 📊 Status")
        if st.session_state.api_key:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ API Key required")
        
        if st.session_state.documents_processed:
            st.success("✅ Documents processed")
        else:
            st.info("ℹ️ No documents uploaded")
        
        if st.session_state.chatbot:
            st.success("✅ Chatbot ready")
        else:
            st.info("ℹ️ Chatbot initializing...")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            if st.session_state.chatbot:
                st.session_state.chatbot.reset_conversation()
            if st.session_state.form_handler:
                st.session_state.form_handler.reset_form()
            st.rerun()

def initialize_chatbot():
    """Initialize the chatbot with current configuration"""
    if not st.session_state.api_key:
        return False
    
    try:
        # Initialize form handler
        if not st.session_state.form_handler:
            st.session_state.form_handler = FormHandler()
        
        # Initialize chatbot
        if not st.session_state.chatbot:
            st.session_state.chatbot = ChatBot(
                api_key=st.session_state.api_key,
                document_processor=st.session_state.document_processor,
                form_handler=st.session_state.form_handler
            )
        
        return True
    except Exception as e:
        st.error(f"Error initializing chatbot: {str(e)}")
        return False

def display_message(message, is_user=True):
    """Display a chat message"""
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 Assistant:</strong> {message}
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 ML Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Document Q&A & Appointment Booking Assistant</p>', unsafe_allow_html=True)
    
    # Setup sidebar
    setup_sidebar()
    
    # Main chat interface
    if not st.session_state.api_key:
        st.warning("Please enter your Google Gemini API Key in the sidebar to get started.")
        st.info("""
        To get your API key:
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Create a new API key
        3. Copy and paste it in the sidebar
        """)
        return
    
    # Initialize chatbot
    if not initialize_chatbot():
        st.error("Failed to initialize chatbot. Please check your API key.")
        return
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(message["content"], message["role"] == "user")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your documents or say 'call me' to book an appointment..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_message(prompt, True)
        
        # Get bot response
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chatbot.get_response(prompt)
                
                # Add bot response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                display_message(response, False)
                
                # Auto-scroll to bottom
                st.rerun()
                
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                display_message(error_msg, False)
    
    # Instructions
    if not st.session_state.messages:
        st.markdown("""
        ### 🚀 Getting Started
        
        **For Document Q&A:**
        - Upload documents using the sidebar
        - Ask questions about the content
        - Example: "What is the main topic discussed in the document?"
        
        **For Appointment Booking:**
        - Say "call me" or "book appointment"
        - I'll collect your information step by step
        - Supports natural date formats like "next Monday"
        
        **Sample Questions:**
        - "Summarize the key points from the document"
        - "Schedule a call with me"
        - "What does the document say about [topic]?"
        - "Book an appointment for tomorrow at 2 PM"
        """)

if __name__ == "__main__":
    main()