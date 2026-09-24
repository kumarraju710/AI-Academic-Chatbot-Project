"""
JNTUK Chatbot - Complete Integration
====================================
Deterministic rule-based chatbot merged with legacy code.
All responses from JSON data only. No random generation.
"""

import google.generativeai as genai
import os
import json
import random
import re
from difflib import SequenceMatcher

# ============================================================
# GEMINI API CONFIGURATION
# ============================================================

GENAI_API_KEY = os.environ.get('GENAI_API_KEY', None)
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)


def get_gemini_response(user_message):
    """Fetch response from Gemini API if configured."""
    if not GENAI_API_KEY:
        return None

    env_model = os.environ.get('GENAI_MODEL')
    fallbacks = [m for m in ([env_model] if env_model else []) + 
                 ['gemini-1.5-flash', 'gemini-pro', 'chat-bison@001'] if m]

    last_exc = None
    for model_name in fallbacks:
        try:
            model = genai.GenerativeModel(model_name)
            try:
                response = model.generate_content(user_message)
            except TypeError:
                response = model.generate(user_message)

            if hasattr(response, 'text'):
                return response.text
            if isinstance(response, dict) and 'content' in response:
                return response['content']
            return str(response)
        except Exception as e:
            last_exc = e
            msg = str(e).lower()
            if any(x in msg for x in ['billing', 'quota', 'permission', 'not authorized']):
                return None
            continue
    
    return None


# ============================================================
# LOAD JSON DATA
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAQ_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'faq.json')
COLLEGE_DATA_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'colleges_data.json')
KEYWORDS_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'colleges_keywords_data.json')

# load FAQ data safely
try:
    with open(FAQ_PATH, 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
except Exception:
    faq_data = {}

# load main college dataset
try:
    with open(COLLEGE_DATA_PATH, 'r', encoding='utf-8') as f:
        colleges_data = json.load(f)
except Exception:
    colleges_data = []

# load keywords dataset and build lookup maps
college_keywords = {}          # maps keyword -> college name (lowercase)
college_name_map = {}          # maps college name (lowercase) -> college object

# populate name map from colleges_data
for _c in colleges_data:
    college_name_map[_c['name'].lower()] = _c

try:
    with open(KEYWORDS_PATH, 'r', encoding='utf-8') as f:
        kw_list = json.load(f)
        for entry in kw_list:
            name = entry.get('college', '').lower()
            # if the college from keywords isn't in the main list yet, skip it
            if name not in college_name_map:
                continue
            for kw in entry.get('keywords', []):
                college_keywords[kw.lower()] = name
except Exception:
    # missing file or parse error should just leave map empty
    college_keywords = {}


# ============================================================
# DETERMINISTIC RESPONSE FUNCTIONS
# ============================================================

def _word_contains(text, phrase):
    """Return True if *phrase* appears in *text* as a separate word or phrase.

    Matching is case‑insensitive and uses word boundaries so that short tokens
    like "ai" do not accidentally match "paid" or "fair".  Multi‑word phrases
    are supported as well.
    """
    return re.search(r"\b" + re.escape(phrase) + r"\b", text) is not None


def find_college(user_message, colleges_list):
    """Find college from user message using multiple strategies.

    The matching order is:
    1. explicit keywords from the keywords JSON file (abbreviations, nicknames)
    2. direct substring match of the full college name
    3. token-based match on significant parts of the name
    4. fuzzy similarity on the entire name
    """
    if not colleges_list:
        return None

    msg_lower = user_message.lower()

    # 0. keyword map lookup (most precise)
    for kw, name in college_keywords.items():
        if _word_contains(msg_lower, kw):
            # return the canonical college object
            return college_name_map.get(name)

    # 1. Direct substring match
    for college in colleges_list:
        if college['name'].lower() in msg_lower:
            return college

    # 2. Token-based match
    skip_words = {'college', 'engineering', 'of', 'technology', 'and', '&', 'the', 'institute', 'a', 'an'}
    for college in colleges_list:
        tokens = college['name'].lower().split()
        for token in tokens:
            if token not in skip_words and len(token) > 2 and _word_contains(msg_lower, token):
                return college

    # 3. Fuzzy match
    best_college = None
    best_score = 0.0
    for college in colleges_list:
        score = SequenceMatcher(None, msg_lower, college['name'].lower()).ratio()
        if score > best_score and score > 0.6:
            best_score = score
            best_college = college

    return best_college


def find_course(user_message, college):
    """Extract course name from message using boundary matches."""
    if not college or not college.get('courses'):
        return None

    msg_lower = user_message.lower()
    for course in college['courses']:
        if _word_contains(msg_lower, course['name'].lower()):
            return course

    return None


def format_college_list(colleges_list):
    """Format all colleges as numbered list."""
    lines = ["Available Colleges under JNTUK:\n"]
    for idx, college in enumerate(colleges_list, start=1):
        lines.append(f"{idx}. {college['name']} – {college['location']}")
    return "\n".join(lines)


def format_college_details(college):
    """Format complete college details."""
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


def format_fee_structure(college):
    """Format complete fee structure."""
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
    """Format semester-wise fees."""
    lines = [
        f"College: {college['name']}",
        "",
        "Semester-wise Fees:",
        ""
    ]
    
    for idx, course in enumerate(college['courses'], start=1):
        semester_fee = course['fee'] // 2
        lines.append(f"{idx}. {course['name']} – Annual ₹{course['fee']:,} | Semester ₹{semester_fee:,}")
    
    lines.extend([
        "",
        f"Deadline: {college['deadline']}",
        f"Late Fee: ₹{college['late_fee']} per week"
    ])
    
    return "\n".join(lines)


def format_specific_course_fee(college, course):
    """Format fee for specific course."""
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


def detect_list_colleges_intent(msg):
    """Detect if user wants college list using word-boundary keywords."""
    keywords = [
        "list colleges", "affiliated colleges", "show colleges",
        "college list", "jntuk colleges", "colleges under jntuk",
        "list all colleges", "show all colleges"
    ]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_fee_structure_intent(msg):
    """Detect if user wants fee structure using word-boundary keywords."""
    keywords = [
        "fee structure", "all fees", "course fees", "branch fees",
        "all branch fees", "fee breakdown", "fee details"
    ]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_semester_fee_intent(msg):
    """Detect if user wants semester fees using boundaries."""
    keywords = ["semester fee", "per semester", "semester wise fee"]
    return any(_word_contains(msg, kw) for kw in keywords)


def get_chatbot_response(user_message, colleges_list, intents):
    """
    Main deterministic response generator.
    
    PRIORITY ORDER:
    1. List all colleges
    2. Find specific college
    3. Detect course fee
    4. Detect semester fee
    5. Detect fee structure
    6. Return college details
    7. Greeting / General
    8. Fallback
    """
    
    if not user_message or not user_message.strip():
        return "Please ask about colleges, fees, courses, or deadlines."
    
    msg = user_message.strip().lower()
    
    # 1. LIST ALL COLLEGES
    if detect_list_colleges_intent(msg):
        return format_college_list(colleges_list)
    
    # 2. FIND SPECIFIC COLLEGE
    college = find_college(msg, colleges_list)
    
    if college:
        # 2a. Specific course?
        course = find_course(msg, college)
        if course:
            return format_specific_course_fee(college, course)
        
        # 2b. Fee structure?
        if detect_fee_structure_intent(msg):
            return format_fee_structure(college)
        
        # 2c. Semester fees?
        if detect_semester_fee_intent(msg):
            return format_semester_fees(college)
        
        # 2d. Default college details
        return format_college_details(college)
    
    # 3. COLLEGE MENTIONED BUT NOT FOUND
    if any(_word_contains(msg, word) for word in ['college', 'fee', 'admission', 'deadline', 'course']):
        return "Sorry, this college information is currently unavailable. We are working to add it soon."
    
    # 4. FALLBACK
    return "I'm here to help with JNTUK college information. Please ask about colleges, fees, courses, or deadlines."


# ============================================================
# LEGACY COMPATIBILITY
# ============================================================

try:
    from users.models import FAQ
    
    def find_best_faq(user_message):
        """Legacy FAQ lookup."""
        try:
            faqs = FAQ.objects.all()
            best_match = None
            best_score = 0
            for faq in faqs:
                score = SequenceMatcher(None, user_message.lower(), faq.question.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_match = faq
            if best_score > 0.5 and best_match:
                if isinstance(best_match.answer, list):
                    return best_match.answer[0]
                elif isinstance(best_match.answer, str):
                    try:
                        ans_list = json.loads(best_match.answer)
                        if isinstance(ans_list, list) and ans_list:
                            return ans_list[0]
                        return best_match.answer
                    except:
                        return best_match.answer
            return None
        except:
            return None
except:
    def find_best_faq(user_message):
        return None


# ============================================================
# PUBLIC API
# ============================================================

def get_bot_response(user_message):
    """
    Main entry point for chatbot.
    
    Tries Gemini first if configured, then falls back to
    deterministic rule-based logic.
    """
    
    # Try Gemini if available
    if GENAI_API_KEY:
        gemini_resp = get_gemini_response(user_message)
        if gemini_resp:
            return gemini_resp
    
    # Deterministic JSON-based response
    return get_chatbot_response(user_message, colleges_data, faq_data)
