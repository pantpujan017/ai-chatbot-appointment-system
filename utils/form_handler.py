# utils/form_handler.py
import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError

class FormHandler:
    def __init__(self):
        self.form_fields = {
            'name': None,
            'phone': None,
            'email': None,
            'appointment_date': None,
            'appointment_time': None,
            'purpose': None
        }
        self.form_state = 'idle'  # idle, collecting, complete
        self.current_field = None
        
    def start_form_collection(self):
        """Start the form collection process"""
        self.form_state = 'collecting'
        self.current_field = 'name'
        return "I'd be happy to help you schedule a call. Let me collect some information from you. What's your full name?"
    
    def process_form_input(self, user_input):
        """Process user input for form fields"""
        if self.form_state != 'collecting':
            return "Form collection is not active."
        
        if self.current_field == 'name':
            return self._process_name(user_input)
        elif self.current_field == 'phone':
            return self._process_phone(user_input)
        elif self.current_field == 'email':
            return self._process_email(user_input)
        elif self.current_field == 'appointment_date':
            return self._process_appointment_date(user_input)
        elif self.current_field == 'appointment_time':
            return self._process_appointment_time(user_input)
        elif self.current_field == 'purpose':
            return self._process_purpose(user_input)
        
        return "Unknown field being processed."
    
    def _process_name(self, name):
        """Process and validate name input"""
        name = name.strip()
        
        if len(name) < 2:
            return "Please provide your full name (at least 2 characters)."
        
        if not re.match(r'^[a-zA-Z\s\-\.\']+$', name):
            return "Please provide a valid name using only letters, spaces, hyphens, dots, and apostrophes."
        
        self.form_fields['name'] = name
        self.current_field = 'phone'
        return f"Thank you, {name}! Now, please provide your phone number."
    
    def _process_phone(self, phone):
        """Process and validate phone number"""
        phone = phone.strip()
        
        try:
            # Try to parse phone number
            parsed_phone = phonenumbers.parse(phone, "US")  # Default to US, can be adjusted
            
            if not phonenumbers.is_valid_number(parsed_phone):
                return "Please provide a valid phone number."
            
            # Format phone number
            formatted_phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.NATIONAL)
            
            self.form_fields['phone'] = formatted_phone
            self.current_field = 'email'
            return f"Got it! Your phone number is {formatted_phone}. What's your email address?"
            
        except phonenumbers.NumberParseException:
            return "Please provide a valid phone number (e.g., +1-234-567-8900 or (234) 567-8900)."
    
    def _process_email(self, email):
        """Process and validate email address"""
        email = email.strip().lower()
        
        try:
            # Validate email
            validated_email = validate_email(email)
            normalized_email = validated_email.email
            
            self.form_fields['email'] = normalized_email
            self.current_field = 'appointment_date'
            return f"Perfect! Your email is {normalized_email}. When would you like to schedule the appointment? (You can say things like 'next Monday', 'tomorrow', or provide a specific date)"
            
        except EmailNotValidError:
            return "Please provide a valid email address (e.g., john@example.com)."
    
    def _process_appointment_date(self, date_input):
        """Process appointment date with date extraction"""
        from .date_extractor import DateExtractor
        
        date_extractor = DateExtractor()
        extracted_date = date_extractor.extract_date(date_input)
        
        if not extracted_date:
            return "I couldn't understand the date. Please provide a date like 'next Monday', 'tomorrow', or in YYYY-MM-DD format."
        
        is_valid, message = date_extractor.validate_date(extracted_date)
        
        if not is_valid:
            return f"Invalid date: {message}. Please provide a future date."
        
        self.form_fields['appointment_date'] = extracted_date
        formatted_date = date_extractor.format_date_display(extracted_date)
        
        self.current_field = 'appointment_time'
        return f"Great! I've scheduled it for {formatted_date}. What time would you prefer? (e.g., 10:00 AM, 2:30 PM)"
    
    def _process_appointment_time(self, time_input):
        """Process and validate appointment time"""
        time_input = time_input.strip().upper()
        
        # Basic time validation patterns
        time_patterns = [
            r'^([0-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)$',  # 12-hour format
            r'^([0-9]|1[0-9]|2[0-3]):[0-5][0-9]$',     # 24-hour format
            r'^([0-9]|1[0-2])\s?(AM|PM)$',             # Hour only 12-hour
        ]
        
        valid_time = False
        for pattern in time_patterns:
            if re.match(pattern, time_input):
                valid_time = True
                break
        
        if not valid_time:
            return "Please provide a valid time format (e.g., 10:00 AM, 14:30, or 2 PM)."
        
        self.form_fields['appointment_time'] = time_input
        self.current_field = 'purpose'
        return f"Perfect! Time set for {time_input}. Finally, could you briefly tell me the purpose of this call or meeting?"
    
    def _process_purpose(self, purpose):
        """Process the purpose of the appointment"""
        purpose = purpose.strip()
        
        if len(purpose) < 5:
            return "Please provide a brief description of the purpose (at least 5 characters)."
        
        self.form_fields['purpose'] = purpose
        self.form_state = 'complete'
        self.current_field = None
        
        return self._generate_confirmation()
    
    def _generate_confirmation(self):
        """Generate confirmation message with all collected information"""
        confirmation = f"""
Perfect! I've collected all the information. Here's your appointment summary:

📝 **Appointment Details:**
• **Name:** {self.form_fields['name']}
• **Phone:** {self.form_fields['phone']}
• **Email:** {self.form_fields['email']}
• **Date:** {self.form_fields['appointment_date']}
• **Time:** {self.form_fields['appointment_time']}
• **Purpose:** {self.form_fields['purpose']}

Your appointment has been scheduled! Someone from our team will call you at the specified date and time. You'll also receive a confirmation email shortly.

Is there anything else I can help you with?
        """
        
        return confirmation.strip()
    
    def reset_form(self):
        """Reset the form to initial state"""
        self.form_fields = {key: None for key in self.form_fields}
        self.form_state = 'idle'
        self.current_field = None
    
    def get_form_status(self):
        """Get current form collection status"""
        return {
            'state': self.form_state,
            'current_field': self.current_field,
            'fields': self.form_fields.copy()
        }
    
    def is_form_complete(self):
        """Check if form collection is complete"""
        return self.form_state == 'complete'
    
    def is_collecting(self):
        """Check if currently collecting form data"""
        return self.form_state == 'collecting'