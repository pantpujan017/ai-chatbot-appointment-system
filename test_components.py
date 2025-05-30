# test_components.py
"""
Test script to verify individual components are working correctly.
Run this before starting the main application to ensure everything is set up properly.
"""

import os
from utils.date_extractor import DateExtractor
from utils.form_handler import FormHandler

def test_date_extractor():
    """Test the date extraction functionality"""
    print("🗓️ Testing Date Extractor...")
    
    date_extractor = DateExtractor()
    test_cases = [
        "tomorrow",
        "next Monday", 
        "this Friday",
        "2024-12-25",
        "January 15, 2024",
        "in 3 days",
        "next week"
    ]
    
    for test_case in test_cases:
        result = date_extractor.extract_date(test_case)
        print(f"  '{test_case}' -> {result}")
    
    print("✅ Date Extractor test completed\n")

def test_form_handler():
    """Test the form handler functionality"""
    print("📝 Testing Form Handler...")
    
    form_handler = FormHandler()
    
    # Test form initialization
    response = form_handler.start_form_collection()
    print(f"  Form start: {response[:50]}...")
    
    # Test name processing
    response = form_handler.process_form_input("John Smith")
    print(f"  Name input: {response[:50]}...")
    
    # Test phone processing
    response = form_handler.process_form_input("(555) 123-4567")
    print(f"  Phone input: {response[:50]}...")
    
    print("✅ Form Handler test completed\n")

def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment...")
    
    # Check for required modules
    try:
        import streamlit
        print("  ✅ Streamlit installed")
    except ImportError:
        print("  ❌ Streamlit not installed")
    
    try:
        import langchain
        print("  ✅ LangChain installed")
    except ImportError:
        print("  ❌ LangChain not installed")
    
    try:
        import google.generativeai
        print("  ✅ Google GenerativeAI installed")
    except ImportError:
        print("  ❌ Google GenerativeAI not installed")
    
    try:
        import faiss
        print("  ✅ FAISS installed")
    except ImportError:
        print("  ❌ FAISS not installed")
    
    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print("  ✅ Google API Key found in environment")
    else:
        print("  ⚠️ Google API Key not found in environment (you can set it in the app)")
    
    print("✅ Environment test completed\n")

def main():
    """Run all tests"""
    print("🚀 Starting Component Tests...\n")
    
    test_environment()
    test_date_extractor()
    test_form_handler()
    
    print("🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Make sure you have your Google Gemini API key")
    print("2. Run: streamlit run app.py")
    print("3. Upload some documents and start chatting!")

if __name__ == "__main__":
    main()