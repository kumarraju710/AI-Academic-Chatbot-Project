"""
Enhanced Chatbot V3 - Context-Aware
=====================================
Complete chatbot implementation with:
- College list display (numbered)
- Selected college tracking
- Context-aware responses  
- Detailed college information
- Semester-wise fee structure
- Late fee and deadline information
- Branch-specific queries
"""

import os
import json
import re
from difflib import SequenceMatcher
from .chatbot_context import get_user_context


# ============================================================
# LOAD JSON DATA
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLEGE_DATA_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'colleges_data.json')
KEYWORDS_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'colleges_keywords_data.json')

# Load colleges data
try:
    with open(COLLEGE_DATA_PATH, 'r', encoding='utf-8') as f:
        colleges_data = json.load(f)
except Exception as e:
    print(f"Error loading colleges data: {e}")
    colleges_data = []

# Build lookup maps
college_name_map = {}  # maps college name (lowercase) -> college object
college_keywords = {}  # maps keyword -> college name (lowercase)

for college in colleges_data:
    college_name_map[college['name'].lower()] = college

try:
    with open(KEYWORDS_PATH, 'r', encoding='utf-8') as f:
        kw_list = json.load(f)
        for entry in kw_list:
            name = entry.get('college', '').lower()
            if name not in college_name_map:
                continue
            for kw in entry.get('keywords', []):
                college_keywords[kw.lower()] = name
except Exception:
    college_keywords = {}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def _word_contains(text, phrase):
    """Check if phrase appears in text as separate word (case-insensitive)."""
    return re.search(r"\b" + re.escape(phrase) + r"\b", text, re.IGNORECASE) is not None


def find_college(user_message, colleges_list):
    """
    Find college from user message using multiple strategies:
    1. Keywords from JSON
    2. Direct substring match
    3. Token-based match
    4. Fuzzy similarity
    """
    if not colleges_list:
        return None

    msg_lower = user_message.lower()

    # Strategy 1: Keyword map lookup
    for kw, name in college_keywords.items():
        if _word_contains(msg_lower, kw):
            return college_name_map.get(name)

    # Strategy 2: Direct substring match
    for college in colleges_list:
        if college['name'].lower() in msg_lower:
            return college

    # Strategy 3: Token-based match
    skip_words = {'college', 'engineering', 'of', 'technology', 'and', '&', 'the', 
                  'institute', 'a', 'an', 'university', 'school'}
    for college in colleges_list:
        tokens = college['name'].lower().split()
        for token in tokens:
            if token not in skip_words and len(token) > 2 and _word_contains(msg_lower, token):
                return college

    # Strategy 4: Fuzzy match
    best_college = None
    best_score = 0.0
    for college in colleges_list:
        score = SequenceMatcher(None, msg_lower, college['name'].lower()).ratio()
        if score > best_score and score > 0.6:
            best_score = score
            best_college = college

    return best_college


def find_course(user_message, college):
    """Find course from user message."""
    if not college or not college.get('courses'):
        return None

    msg_lower = user_message.lower()
    for course in college['courses']:
        if _word_contains(msg_lower, course['name'].lower()):
            return course
    return None


# ============================================================
# INTENT DETECTION FUNCTIONS
# ============================================================

def detect_list_colleges_intent(msg):
    """Detect if user wants to see college list."""
    keywords = [
        "list of colleges", "list all colleges", "show colleges", "show all colleges",
        "available colleges", "colleges list", "college list", "affiliated colleges",
        "jntuk colleges", "colleges under jntuk"
    ]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_college_details_intent(msg):
    """Detect if user wants general college details."""
    keywords = ["about", "details", "tell me about", "info", "information"]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_placement_intent(msg):
    """Detect if user wants placement details."""
    keywords = ["placement", "packages", "companies", "recruiters", "recruitment", "jobs"]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_environment_intent(msg):
    """Detect if user wants environment/campus info."""
    keywords = ["environment", "campus", "facilities", "infrastructure", "hostel", "labs"]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_fee_structure_intent(msg):
    """Detect if user wants fee structure for all branches."""
    keywords = ["fee structure", "all fees", "course fees", "branch fees", "all branch fees"]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_semester_fee_intent(msg):
    """Detect if user wants semester-wise fees."""
    keywords = ["semester fee", "per semester", "semester wise", "semester-wise"]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_enrollment_intent(msg):
    """Detect if user wants enrollment information."""
    keywords = ["enrollment", "enroll", "admission", "register", "registration", "how to join"]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_deadline_intent(msg):
    """Detect if user wants deadline information."""
    keywords = ["deadline", "due date", "last date", "when", "fee deadline"]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_late_fee_intent(msg):
    """Detect if user wants late fee information."""
    keywords = ["late fee", "late charges", "penalty", "penalties", "fine"]
    return any(_word_contains(msg, kw) for kw in keywords)


def detect_required_documents_intent(msg):
    """Detect if user is asking about required admission documents."""
    keywords = [
        "required documents", "documents needed", "what documents",
        "document list", "docs required", "documents required",
        "needed papers", "upload documents", "paperwork"
    ]
    return any(_word_contains(msg, kw) for kw in keywords)


# ============================================================
# FORMATTING FUNCTIONS
# ============================================================

def format_colleges_list(colleges_list):
    """Format all colleges as numbered list."""
    lines = ["📚 **These are the colleges list, which I give the information:**\n"]
    for idx, college in enumerate(colleges_list, start=1):
        lines.append(f"{idx}. {college['name']} – {college['location']}")
    
    lines.append("\n💡 **Tip:** Select a college to view details and fees!\n")
    return "\n".join(lines)


def format_college_details(college):
    """Format complete college details with about, placements, and environment."""
    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🎓 **{college['name']}**",
        f"📍 Location: {college['location']}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        
        f"**📝 About the College:**",
        f"{college.get('about', 'Information not available')}\n",
        
        f"**💼 Placement Details:**",
        f"{college.get('placement_details', 'Information not available')}\n",
        
        f"**🏛️ Campus Environment:**",
        f"{college.get('environment', 'Information not available')}\n",
        
        f"**📅 Important Dates:**",
        f"• Registration: {college.get('registration_start', 'N/A')} to {college.get('registration_end', 'N/A')}",
        f"• Fee Deadline: {college.get('deadline', 'N/A')}",
        f"• Late Fee: ₹{college.get('late_fee', 0)}\n",
        
        f"**📚 Available Courses & Fees:**\n"
    ]
    
    for idx, course in enumerate(college['courses'], start=1):
        lines.append(f"{idx}. {course['name']} – ₹{course['fee']:,}/year (Seats: {course.get('seats', 'N/A')})")
    
    lines.append(f"\n💡 Ask about specific courses or semester fees!")
    return "\n".join(lines)


def format_all_branches_fees(college):
    """Format all branches with fees in organized manner."""
    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"💰 **{college['name']} - All Branches & Fee Structure**",
        f"📍 Location: {college['location']}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    ]
    
    for idx, course in enumerate(college['courses'], start=1):
        semester_fee = course['fee'] // 2
        lines.append(
            f"{idx}. {course['name']:<20} – Annual: ₹{course['fee']:>8,} | "
            f"Semester: ₹{semester_fee:>8,}"
        )
    
    lines.extend([
        f"\n📅 **Fee Deadline:** {college.get('deadline', 'N/A')}",
        f"⚠️ **Late Fee Penalty:** ₹{college.get('late_fee', 0)}"
    ])
    
    return "\n".join(lines)


def format_semester_wise_fees(college):
    """Format semester-wise fee breakdown for all branches."""
    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 **{college['name']} - Semester-wise Fee Structure**",
        f"📍 Location: {college['location']}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    ]
    
    for idx, course in enumerate(college['courses'], start=1):
        annual_fee = course['fee']
        sem_fee = annual_fee // 2
        
        lines.append(f"**{idx}. {course['name']}**")
        lines.append(f"   • Semester 1: ₹{sem_fee:,}")
        lines.append(f"   • Semester 2: ₹{sem_fee:,}")
        lines.append(f"   • Annual Total: ₹{annual_fee:,}\n")
    
    lines.extend([
        f"📅 **Registration Period:** {college.get('registration_start', 'N/A')} to {college.get('registration_end', 'N/A')}",
        f"📌 **Fee Deadline:** {college.get('deadline', 'N/A')}",
        f"⚠️ **Late Fee:** ₹{college.get('late_fee', 0)}"
    ])
    
    return "\n".join(lines)


def format_specific_course_details(college, course):
    """Format detailed information for a specific course."""
    semester_fee = course['fee'] // 2
    
    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📖 **{course['name']} at {college['name']}**",
        f"📍 {college['location']}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        
        f"💰 **Fee Information:**",
        f"• Annual Fee: ₹{course['fee']:,}",
        f"• Semester Fee: ₹{semester_fee:,}",
        f"• Available Seats: {course.get('seats', 'N/A')}\n",
        
        f"📅 **Important Dates:**",
        f"• Registration Opens: {college.get('registration_start', 'N/A')}",
        f"• Registration Closes: {college.get('registration_end', 'N/A')}",
        f"• Fee Deadline: {college.get('deadline', 'N/A')}",
        f"• Late Fee Penalty: ₹{college.get('late_fee', 0)}\n",
        
        f"💡 **Ask about:** Placement details, campus facilities, enrollment process"
    ]
    
    return "\n".join(lines)


def format_enrollment_info(college):
    """Format enrollment process information."""
    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓",
        f"📝 **Enrollment Process at {college['name']}**",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        
        f"**Step 1: Registration Period**",
        f"• Opens: {college.get('registration_start', 'N/A')}",
        f"• Closes: {college.get('registration_end', 'N/A')}\n",
        
        f"**Step 2: Online Registration**",
        f"• Register on the university/college portal",
        f"• Select your preferred course/branch",
        f"• Upload required documents\n",
        
        f"**Step 3: Payment**",
        f"• Pay the course-specific fee",
        f"• Use UPI, net banking, credit/debit card, or challan",
        f"• Payment must be completed by {college.get('deadline', 'the deadline')}\n",
        
        f"**Step 4: Confirmation**",
        f"• Keep payment receipt safe",
        f"• Receive enrollment confirmation",
        f"• Download acknowledgment\n",
        
        f"⚠️ **Important:** Late enrollments attract ₹{college.get('late_fee', 0)} penalty per week!"
    ]
    
    return "\n".join(lines)


def format_required_documents(college=None):
    """Return a bullet list of common documents needed for admission.

    College-specific note is added when a college object is provided.
    """
    docs = [
        "10th grade mark sheet",
        "12th grade mark sheet",
        "Transfer Certificate (TC)",
        "Migration Certificate (if applicable)",
        "Passport-size photos (4-6)",
        "Proof of identity (Aadhar/Passport/Driver's license)",
        "Proof of residence",
        "Caste/Category certificate (if applicable)",
        "Any other documents specified by the college"
    ]
    lines = ["📄 **Documents Required for Admission:**"]
    for idx, item in enumerate(docs, start=1):
        lines.append(f"{idx}. {item}")

    if college:
        lines.append(f"\n*Please submit these documents during registration at {college['name']}." )
    else:
        lines.append("\n*Please check with the specific college for any additional requirements.")

    return "\n".join(lines)


# ============================================================
# MAIN BOT LOGIC
# ============================================================

def get_enhanced_response(user_message, user_id=None):
    """
    Generate context-aware response.
    
    Flow:
    1. Check for college list or document requests
    2. Try to find college from message
    3. If college found, save to context and show details
    4. If college already selected, answer context-specific questions
    5. Provide helpful prompts and fallback
    """

    # get or create user context (used for history and selected college)
    context = get_user_context(user_id) if user_id else None

    # validation
    if not user_message or not user_message.strip():
        reply = "👋 Hello! I can help you with information for some specific colleges, type 'list of colleges' to see all available colleges."
    else:
        msg = user_message.strip()
        msg_lower = msg.lower()
        reply = None

        # 1. List colleges
        if detect_list_colleges_intent(msg_lower):
            reply = format_colleges_list(colleges_data)

        # 1b. Required documents question
        elif detect_required_documents_intent(msg_lower):
            # try find a college mentioned or use context
            college = find_college(msg, colleges_data)
            if not college and context:
                college = context.get_selected_college()
            reply = format_required_documents(college)

        else:
            # 2. Look for specific college mentioned
            college = find_college(msg, colleges_data)

            if college:
                if context:
                    context.set_selected_college(college)

                course = find_course(msg, college)
                if course:
                    reply = format_specific_course_details(college, course)
                elif detect_placement_intent(msg_lower) or detect_environment_intent(msg_lower):
                    reply = format_college_details(college)
                elif detect_semester_fee_intent(msg_lower):
                    reply = format_semester_wise_fees(college)
                elif detect_fee_structure_intent(msg_lower):
                    reply = format_all_branches_fees(college)
                elif detect_enrollment_intent(msg_lower):
                    reply = format_enrollment_info(college)
                elif detect_deadline_intent(msg_lower) or detect_late_fee_intent(msg_lower):
                    lines = [
                        f"📅 **Deadline Information for {college['name']}**\n",
                        f"Fee Payment Deadline: {college.get('deadline', 'Not specified')}",
                        f"Late Fee Penalty: ₹{college.get('late_fee', 0)}",
                        f"Registration Period: {college.get('registration_start', 'N/A')} to {college.get('registration_end', 'N/A')}"
                    ]
                    reply = "\n".join(lines)
                else:
                    reply = format_college_details(college)
            else:
                # 3. use context if available
                if context and context.get_selected_college():
                    college = context.get_selected_college()
                    if detect_placement_intent(msg_lower) or detect_environment_intent(msg_lower):
                        reply = format_college_details(college)
                    elif detect_fee_structure_intent(msg_lower):
                        reply = format_all_branches_fees(college)
                    elif detect_semester_fee_intent(msg_lower):
                        reply = format_semester_wise_fees(college)
                    elif detect_enrollment_intent(msg_lower):
                        reply = format_enrollment_info(college)
                    else:
                        course = find_course(msg, college)
                        if course:
                            reply = format_specific_course_details(college, course)

                # 4. college mentioned but not in our data
                if reply is None and any(_word_contains(msg_lower, word) for word in ['college', 'university', 'course', 'fee', 'admission', 'branch']):
                    reply = (
                        f"❌ **College Not Found**\n\n"
                        f"The college you're looking for is not currently in our database. "
                        f"Please type 'list colleges' to see available colleges, or try searching with different keywords.\n\n"
                        f"💡 Available: Aditya,RVR & JC, GMRIT, GIET,Helapuri,CR Reddy, Eluru college,Ramachandra"
                    )

                # 5. fallback if nothing matched
                if reply is None:
                    reply = (
                        f"👋 I'm here to help with some colleges,type list of colleges to get the colleges list!\n\n"
                        f"**You can ask about:**\n"
                        f"• List of colleges\n"
                        f"• College details (about, placements, environment)\n"
                        f"• Fee structure (annual, semester-wise, by branch)\n"
                        f"• Enrollment process\n"
                        f"• Deadlines and late fees\n\n"
                        f"**Try:** 'list colleges' or 'tell me about [college name]'"
                    )

    # record query/response in context history with a cap
    if context and reply is not None:
        context.add_to_history(user_message, reply)
        # enforce limit (50 entries)
        if len(context.conversation_history) > 50:
            context.conversation_history = context.conversation_history[-50:]

    return reply


# Public API
def get_bot_response(user_message, user_id=None):
    """Main entry point for chatbot responses."""
    return get_enhanced_response(user_message, user_id)
