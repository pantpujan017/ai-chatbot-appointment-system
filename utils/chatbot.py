# utils/chatbot.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import re

class ChatBot:
    def __init__(self, api_key, document_processor=None, form_handler=None):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        self.document_processor = document_processor
        self.form_handler = form_handler
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize agent with tools
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
    def _create_tools(self):
        """Create tools for the agent"""
        tools = []
        
        # Document Q&A tool
        if self.document_processor:
            def document_qa(query: str) -> str:
                """Answer questions based on uploaded documents"""
                relevant_docs = self.document_processor.get_relevant_documents(query)
                
                if not relevant_docs:
                    return "I don't have any relevant information in the uploaded documents to answer this question."
                
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                prompt = f"""
                Based on the following context from uploaded documents, answer the question:
                
                Context:
                {context}
                
                Question: {query}
                
                Please provide a comprehensive answer based only on the information provided in the context.
                If the context doesn't contain enough information to answer the question, say so.
                """
                
                response = self.llm.invoke(prompt)
                return response.content
            
            tools.append(Tool(
                name="DocumentQA",
                description="Use this tool to answer questions based on uploaded documents",
                func=document_qa
            ))
        
        # Appointment booking tool
        if self.form_handler:
            def book_appointment(query: str) -> str:
                """Handle appointment booking and form collection"""
                
                # Check if user wants to book appointment or be called
                booking_keywords = ['call me', 'book appointment', 'schedule call', 'contact me', 'arrange call']
                if any(keyword in query.lower() for keyword in booking_keywords):
                    if not self.form_handler.is_collecting():
                        return self.form_handler.start_form_collection()
                
                # If currently collecting form data
                if self.form_handler.is_collecting():
                    return self.form_handler.process_form_input(query)
                
                return "I can help you schedule an appointment. Just say 'call me' or 'book appointment' to get started!"
            
            tools.append(Tool(
                name="AppointmentBooking",
                description="Use this tool when user wants to book an appointment, schedule a call, or be contacted",
                func=book_appointment
            ))
        
        # General information tool
        def general_chat(query: str) -> str:
            """Handle general conversation and questions"""
            prompt = f"""
            You are a helpful AI assistant. Answer the following question in a friendly and informative way:
            
            Question: {query}
            
            Provide a helpful response. If the user seems to want to book an appointment or be contacted, 
            suggest they can say "call me" or "book appointment".
            """
            
            response = self.llm.invoke(prompt)
            return response.content
        
        tools.append(Tool(
            name="GeneralChat",
            description="Use this tool for general conversation and questions not related to documents or appointments",
            func=general_chat
        ))
        
        return tools
    
    def _create_agent(self):
        """Create the conversational agent"""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def get_response(self, user_input):
        """Get response from the chatbot"""
        try:
            # Check if we're in the middle of form collection
            if self.form_handler and self.form_handler.is_collecting():
                response = self.form_handler.process_form_input(user_input)
                return response
            
            # Check for appointment booking intent
            booking_keywords = ['call me', 'book appointment', 'schedule call', 'contact me', 'arrange call']
            if any(keyword in user_input.lower() for keyword in booking_keywords):
                if self.form_handler:
                    response = self.form_handler.start_form_collection()
                    return response
            
            # Use agent for other queries
            response = self.agent.run(input=user_input)
            return response
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.memory.clear()
        if self.form_handler:
            self.form_handler.reset_form()
    
    def get_conversation_history(self):
        """Get the conversation history"""
        return self.memory.chat_memory.messages
    
    def add_to_history(self, user_message, ai_message):
        """Add messages to conversation history"""
        self.memory.chat_memory.add_user_message(user_message)
        self.memory.chat_memory.add_ai_message(ai_message)