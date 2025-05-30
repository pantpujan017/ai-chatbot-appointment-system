# utils/date_extractor.py
import re
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

class DateExtractor:
    def __init__(self):
        self.today = datetime.now().date()
        
    def extract_date(self, text):
        """Extract date from natural language text"""
        text = text.lower().strip()
        
        # Handle relative dates
        if 'today' in text:
            return self.today.strftime('%Y-%m-%d')
        elif 'tomorrow' in text:
            return (self.today + timedelta(days=1)).strftime('%Y-%m-%d')
        elif 'yesterday' in text:
            return (self.today - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Handle "next" dates
        if 'next' in text:
            return self._handle_next_dates(text)
        
        # Handle "this" dates
        if 'this' in text:
            return self._handle_this_dates(text)
        
        # Handle specific weekdays
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(weekdays):
            if day in text:
                return self._get_next_weekday(i)
        
        # Try to parse absolute dates
        try:
            # Look for date patterns
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
                r'\d{1,2}/\d{1,2}/\d{4}',  # M/D/YYYY
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    try:
                        parsed_date = parse(matches[0])
                        return parsed_date.strftime('%Y-%m-%d')
                    except:
                        continue
            
            # Try general parsing
            parsed_date = parse(text, fuzzy=True)
            return parsed_date.strftime('%Y-%m-%d')
            
        except:
            return None
    
    def _handle_next_dates(self, text):
        """Handle 'next' relative dates"""
        if 'next week' in text:
            return (self.today + timedelta(weeks=1)).strftime('%Y-%m-%d')
        elif 'next month' in text:
            return (self.today + relativedelta(months=1)).strftime('%Y-%m-%d')
        elif 'next year' in text:
            return (self.today + relativedelta(years=1)).strftime('%Y-%m-%d')
        
        # Handle next specific weekday
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(weekdays):
            if f'next {day}' in text:
                return self._get_next_weekday(i, next_week=True)
        
        return None
    
    def _handle_this_dates(self, text):
        """Handle 'this' relative dates"""
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(weekdays):
            if f'this {day}' in text:
                return self._get_this_weekday(i)
        
        return None
    
    def _get_next_weekday(self, weekday, next_week=False):
        """Get the next occurrence of a specific weekday"""
        days_ahead = weekday - self.today.weekday()
        
        if days_ahead <= 0 or next_week:  # Target day already happened this week or explicitly next week
            days_ahead += 7
        
        target_date = self.today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    def _get_this_weekday(self, weekday):
        """Get this week's occurrence of a specific weekday"""
        days_ahead = weekday - self.today.weekday()
        
        if days_ahead < 0:  # If the day already passed this week, get next week
            days_ahead += 7
        
        target_date = self.today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    def validate_date(self, date_string):
        """Validate if a date string is in correct format and not in the past"""
        try:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
            
            if date_obj < self.today:
                return False, "Date cannot be in the past"
            
            return True, "Valid date"
        except ValueError:
            return False, "Invalid date format. Please use YYYY-MM-DD"
    
    def format_date_display(self, date_string):
        """Format date for display"""
        try:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d')
            return date_obj.strftime('%B %d, %Y')  # e.g., "January 15, 2024"
        except:
            return date_string