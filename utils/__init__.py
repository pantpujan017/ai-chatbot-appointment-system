# utils/__init__.py
"""
ML Chatbot Utilities Package

This package contains the core modules for the ML chatbot application:
- document_processor: Handle document loading and vector storage
- chatbot: Main chatbot logic and agent orchestration  
- form_handler: Conversational form collection and validation
- date_extractor: Natural language date parsing and validation
"""

from .document_processor import DocumentProcessor
from .chatbot import ChatBot
from .form_handler import FormHandler
from .date_extractor import DateExtractor

__all__ = [
    'DocumentProcessor',
    'ChatBot', 
    'FormHandler',
    'DateExtractor'
]

__version__ = "1.0.0"