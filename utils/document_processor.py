# utils/document_processor.py
import os
import streamlit as st
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import tempfile

class DocumentProcessor:
    def __init__(self, api_key):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        self.vector_store = None
        
    def load_documents(self, uploaded_files):
        """Load and process uploaded documents"""
        documents = []
        
        for uploaded_file in uploaded_files:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Load document based on file type
                if uploaded_file.name.endswith('.pdf'):
                    loader = PyPDFLoader(tmp_file_path)
                elif uploaded_file.name.endswith('.docx'):
                    loader = Docx2txtLoader(tmp_file_path)
                elif uploaded_file.name.endswith('.txt'):
                    loader = TextLoader(tmp_file_path)
                else:
                    st.warning(f"Unsupported file type: {uploaded_file.name}")
                    continue
                
                docs = loader.load()
                documents.extend(docs)
                
            except Exception as e:
                st.error(f"Error loading {uploaded_file.name}: {str(e)}")
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
        
        return documents
    
    def create_vector_store(self, documents):
        """Create vector store from documents"""
        if not documents:
            return None
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        
        try:
            # Create vector store
            self.vector_store = FAISS.from_documents(
                chunks,
                self.embeddings
            )
            return self.vector_store
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return None
    
    def get_relevant_documents(self, query, k=3):
        """Retrieve relevant documents for a query"""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            st.error(f"Error retrieving documents: {str(e)}")
            return []