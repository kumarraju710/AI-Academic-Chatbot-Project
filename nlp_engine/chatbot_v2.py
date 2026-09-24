"""
Deterministic Rule-Based Chatbot for JNTUK Affiliated Colleges
============================================================

This module provides rule-based chatbot logic that reads strictly
from JSON data (colleges_data.json and intents_data.json).

NO random text generation. NO hardcoded values.
All responses constructed from JSON data only.

Author: Senior Python Django Backend Engineer
Date: 2026
"""

import os
import json
from difflib import SequenceMatcher


# ============================================================
# 1. UTILITY FUNCTIONS
# ============================================================

def load_json(file_path):
    """Load JSON file safely with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not valid JSON")
        return None


def find_college(user_message, colleges_data):
    """
    Find college from user message.
    
    Strategy:
    1. Direct substring match (case-insensitive)
    2. Token-based match on college name components
    3. Fuzzy match using SequenceMatcher
    
    Args:
        user_message: User input text (lowercase)
        colleges_data: List of college dictionaries
    
    Returns:
        College dictionary if found, else None
    """
    if not colleges_data:
        return None
    
    msg_lower = user_message.lower()
    
    # 1. Direct substring match (fastest)
    for college in colleges_data:
        if college['name'].lower() in msg_lower:
            return college
    
    # 2. Token-based match (skip generic words)
    skip_words = {'college', 'engineering', 'institute', 'of', 'technology',
                  'and', '&', 'the', 'a', 'an'}
    
    for college in colleges_data:
        tokens = college['name'].lower().split()
        for token in tokens:
            if token not in skip_words and len(token) > 2:
                if token in msg_lower:
                    return college
    
    # 3. Fuzzy match (low threshold)
    best_college = None
    best_score = 0.0
    
    for college in colleges_data:
        score = SequenceMatcher(None, msg_lower, college['name'].lower()).ratio()
        if score > best_score and score > 0.6:
            best_score = score
            best_college = college
    
    return best_college


def find_course(user_message, college):
    """
    Extract course name from message if mentioned.
    
    Args:
        user_message: User input (lowercase)
        college: College dictionary
    
    Returns:
        Course dictionary if found, else None
    """
    if not college or not college.get('courses'):
        return None
    
    msg_lower = user_message.lower()
    
    for course in college['courses']:
        if course['name'].lower() in msg_lower:
            return course
    
    return None


def format_college_list(colleges_data):
    """
    Format all colleges as a numbered list.
    
    Returns:
        Formatted string
    """
    lines = ["Available Colleges under JNTUK:\n"]
    
    for idx, college in enumerate(colleges_data, start=1):
        lines.append(f"{idx}. {college['name']} – {college['location']}")
    
    return "\n".join(lines)


def format_fee_structure(college):
    """
    Format complete fee structure for a college.
    
    Returns:
        Formatted string with all courses and fees
    """
    lines = [
        f"College: {college['name']}",
        f"Location: {college['location']}",
        "",
        "Fee Structure:",
        ""
    ]
    
    for idx, course in enumerate(college['courses'], start=1):
        lines.append(f"{idx}. {course['name']} – ₹{course['fee']:,} per year")
    
    lines.extend([
        "",
        f"Deadline: {college['deadline']}",
        f"Late Fee: ₹{college['late_fee']} per week"
    ])
    
    return "\n".join(lines)


def format_semester_fees(college):
    """
    Format semester-wise fees for a college.
    
    Semester fee = annual fee / 2
    
    Returns:
        Formatted string
    """
    lines = [
        f"College: {college['name']}",
        "",
        "Semester-wise Fees:",
        ""
    ]
    
    for idx, course in enumerate(college['courses'], start=1):
        semester_fee = course['fee'] // 2
        lines.append(
            f"{idx}. {course['name']} – Annual ₹{course['fee']:,} | "
            f"Semester ₹{semester_fee:,}"
        )
    
    lines.extend([
        "",
        f"Deadline: {college['deadline']}",
        f"Late Fee: ₹{college['late_fee']} per week"
    ])
    
    return "\n".join(lines)


def format_specific_course_fee(college, course):
    """
    Format fee for a specific course.
    
    Returns:
        Formatted string
    """
    semester_fee = course['fee'] // 2
    
    lines = [
        f"College: {college['name']}",
        f"Course: {course['name']}",
        f"Annual Fee: ₹{course['fee']:,}",
        f"Semester Fee: ₹{semester_fee:,}",
        f"Deadline: {college['deadline']}",
        f"Late Fee: ₹{college['late_fee']} per week"
    ]
    
    return "\n".join(lines)


def format_college_details(college):
    """
    Format complete details for a college (all courses and fees).
    
    Returns:
        Formatted string
    """
    lines = [
        f"College: {college['name']}",
        f"Location: {college['location']}",
        "",
        "Courses & Fees:",
        ""
    ]
    
    for idx, course in enumerate(college['courses'], start=1):
        lines.append(f"{idx}. {course['name']} – ₹{course['fee']:,}")
    
    lines.extend([
        "",
        f"Deadline: {college['deadline']}",
        f"Late Fee: ₹{college['late_fee']} per week"
    ])
    
    return "\n".join(lines)


# ============================================================
# 2. INTENT DETECTION (VERY STRICT ORDER)
# ============================================================

def detect_list_colleges_intent(user_message):
    """Detect if user wants list of all colleges."""
    keywords = [
        "list colleges", "affiliated colleges", "show colleges",
        "college list", "jntuk colleges", "colleges under jntuk",
        "list all colleges", "show all colleges"
    ]
    
    msg = user_message.lower()
    for keyword in keywords:
        if keyword in msg:
            return True
    
    return False


def detect_fee_structure_intent(user_message):
    """Detect if user wants full fee structure."""
    keywords = [
        "fee structure", "all fees", "course fees", "branch fees",
        "all branch fees", "fee breakdown", "fee details"
    ]
    
    msg = user_message.lower()
    for keyword in keywords:
        if keyword in msg:
            return True
    
    return False


def detect_semester_fee_intent(user_message):
    """Detect if user wants semester-wise fees."""
    keywords = ["semester fee", "per semester", "semester wise fee"]
    
    msg = user_message.lower()
    for keyword in keywords:
        if keyword in msg:
            return True
    
    return False


def detect_greeting_intent(user_message, intents_data):
    """Detect if user input is a greeting."""
    if not intents_data:
        return None
    
    msg = user_message.lower()
    
    greetings = intents_data.get('greeting', {})
    keywords = greetings.get('keywords', [])
    
    for keyword in keywords:
        if keyword.lower() in msg:
            responses = greetings.get('responses', [])
            return responses[0] if responses else None
    
    return None


# ============================================================
# 3. MAIN CHATBOT RESPONSE FUNCTION (DETERMINISTIC)
# ============================================================

def get_chatbot_response(user_message, colleges_data, intents_data):
    """
    Main function to generate chatbot response.
    
    STRICT INTENT DETECTION ORDER:
    1. List all colleges
    2. Find specific college from message
    3. Detect course and fees
    4. Detect semester fees
    5. Detect fee structure
    6. Return complete college details
    7. Greeting / General response
    8. Fallback message
    
    Args:
        user_message: User input text
        colleges_data: List of college dictionaries (from JSON)
        intents_data: Intent definitions (from JSON)
    
    Returns:
        Formatted response string
    """
    
    # Input validation
    if not user_message or not user_message.strip():
        return "Please ask a question about our colleges, fees, or courses."
    
    msg = user_message.strip().lower()
    
    # ========== PRIORITY 1: LIST ALL COLLEGES ==========
    if detect_list_colleges_intent(msg):
        return format_college_list(colleges_data)
    
    # ========== PRIORITY 2: FIND SPECIFIC COLLEGE ==========
    college = find_college(msg, colleges_data)
    
    if college:
        # College is mentioned. Now check for specific intents.
        
        # 2a. Specific course mentioned?
        course = find_course(msg, college)
        
        if course:
            # User asked about specific course fee
            return format_specific_course_fee(college, course)
        
        # 2b. Fee structure requested?
        if detect_fee_structure_intent(msg):
            return format_fee_structure(college)
        
        # 2c. Semester fees requested?
        if detect_semester_fee_intent(msg):
            return format_semester_fees(college)
        
        # 2d. No specific sub-intent, return complete details
        return format_college_details(college)
    
    # ========== PRIORITY 3: COLLEGE MENTIONED BUT NOT IN DATA ==========
    if any(word in msg for word in ['college', 'fee', 'admission', 'deadline']):
        return (
            "Sorry, this college information is currently unavailable. "
            "We are working to add it soon."
        )
    
    # ========== PRIORITY 4: GREETING / GENERAL ==========
    greeting_response = detect_greeting_intent(msg, intents_data)
    if greeting_response:
        return greeting_response
    
    # ========== PRIORITY 5: FALLBACK ==========
    return (
        "I'm here to help with various colleges information. "
        "Please ask about college details, fees, courses, or deadlines."
    )


# ============================================================
# 4. LOAD DATA AND INITIALIZE
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLEGES_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'colleges_data.json')
INTENTS_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'faq.json')

# Load JSON data
colleges_data = load_json(COLLEGES_PATH)
intents_data = load_json(INTENTS_PATH)


# ============================================================
# 5. PUBLIC API FOR DJANGO VIEWS
# ============================================================

def get_bot_response(user_message):
    """
    Wrapper function for Django views.
    
    Args:
        user_message: User input
    
    Returns:
        Response string
    """
    return get_chatbot_response(user_message, colleges_data, intents_data)


# ============================================================
# 6. TESTING / DEMONSTRATION
# ============================================================

if __name__ == '__main__':
    # Test cases
    test_messages = [
        "list colleges",
        "show me all colleges",
        "aditya college",
        "aditya cse fee",
        "rvr & jc semester fee",
        "gmrit fee structure",
        "cse fees at eluru college",
        "cr reddy college",
        "hello",
        "xyz college fees",
        "tell me about courses",
        "deadline for admission"
    ]
    
    print("=" * 70)
    print("JNTUK CHATBOT - DETERMINISTIC (RULE-BASED) TEST")
    print("=" * 70)
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        print("-" * 70)
        response = get_chatbot_response(msg, colleges_data, intents_data)
        print(f"🤖 Bot:\n{response}")
        print("=" * 70)
