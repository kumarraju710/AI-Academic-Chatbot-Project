"""
Comprehensive Test Suite for Enhanced Chatbot V3
================================================

Tests all requirements:
1. College list in numbered format
2. College details with about, placement, environment
3. Context-specific answers
4. Unavailable college handling
5. Deadline dates
6. Late fee penalties
7. Branch-wise fees
8. Semester-wise fees
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nlp_engine.chatbot_v3 import get_bot_response
from nlp_engine.chatbot_context import get_user_context


def test_list_colleges():
    """Test #1: Show colleges in numbered list format."""
    print("\n" + "="*70)
    print("TEST 1: LIST COLLEGES IN NUMBERED FORMAT")
    print("="*70)
    
    response = get_bot_response("list colleges")
    print(response)
    assert "1." in response, "Should show numbered list"
    assert "Aditya College" in response, "Should show Aditya College"
    assert "Pragati" in response, "Should show Pragati"
    print("✓ PASSED: Colleges displayed in numbered format")


def test_college_details():
    """Test #2: Show college details (about, placements, environment)."""
    print("\n" + "="*70)
    print("TEST 2: COLLEGE DETAILS WITH ABOUT, PLACEMENT, ENVIRONMENT")
    print("="*70)
    
    response = get_bot_response("tell me about Aditya College")
    print(response)
    assert "About" in response or "about" in response, "Should show college about"
    assert "Placement" in response or "placement" in response, "Should show placement details"
    assert "Environment" in response or "environment" in response, "Should show environment"
    print("✓ PASSED: College details shown with all required sections")


def test_branch_wise_fees():
    """Test #7: Show enrollment fees for different branches."""
    print("\n" + "="*70)
    print("TEST 7: ENROLLMENT FEES FOR DIFFERENT BRANCHES")
    print("="*70)
    
    response = get_bot_response("Eluru college fees for all branches")
    print(response)
    assert "CSE" in response, "Should show CSE branch"
    assert "₹" in response, "Should show fees"
    assert "45" in response and "000" in response, "Should show correct fees"
    print("✓ PASSED: Branch-wise fees displayed")


def test_semester_wise_fees():
    """Test #8: Show semester-wise fees."""
    print("\n" + "="*70)
    print("TEST 8: SEMESTER-WISE FEE STRUCTURE")
    print("="*70)
    
    response = get_bot_response("Eluru college semester wise fee")
    print(response)
    assert "Semester" in response, "Should mention semester"
    assert "₹" in response, "Should show fees"
    assert "Annual" in response, "Should show annual total"
    print("✓ PASSED: Semester-wise fees displayed")


def test_deadline_dates():
    """Test #5: Show deadline dates according to college policies."""
    print("\n" + "="*70)
    print("TEST 5: DEADLINE DATES ACCORDING TO COLLEGE POLICIES")
    print("="*70)
    
    response = get_bot_response("what is deadline for Eluru college")
    print(response)
    assert "July 31" in response or "deadline" in response.lower(), "Should show deadline"
    print("✓ PASSED: Deadline dates displayed")


def test_late_fee_penalties():
    """Test #6: Show late fee penalties for specific college."""
    print("\n" + "="*70)
    print("TEST 6: LATE FEE PENALTIES FOR SPECIFIC COLLEGE")
    print("="*70)
    
    response = get_bot_response("Eluru college late fee penalty")
    print(response)
    assert "500" in response or "late fee" in response.lower(), "Should show late fee"
    print("✓ PASSED: Late fee penalties displayed")


def test_unavailable_college():
    """Test #4: Show unavailable message for non-existent college."""
    print("\n" + "="*70)
    print("TEST 4: UNAVAILABLE COLLEGE MESSAGE")
    print("="*70)
    
    response = get_bot_response("tell me about the college that doesn't exist")
    print(response)
    assert "not found" in response.lower() or "unavailable" in response.lower() or "Not Found" in response, \
        "Should show unavailable message"
    print("✓ PASSED: Unavailable college message shown")


def test_specific_course_in_college():
    """Test #3: Answer specific questions about selected course."""
    print("\n" + "="*70)
    print("TEST 3: SPECIFIC COURSE DETAILS")
    print("="*70)
    
    response = get_bot_response("CSE fee at Eluru college")
    print(response)
    assert "CSE" in response, "Should mention CSE"
    assert "Eluru" in response, "Should mention college"
    assert "₹" in response, "Should show fee"
    print("✓ PASSED: Specific course details shown")


def test_enrollment_process():
    """Test: Show enrollment process for selected college."""
    print("\n" + "="*70)
    print("TEST: ENROLLMENT PROCESS")
    print("="*70)
    
    response = get_bot_response("enrollment process at Eluru college")
    print(response)
    assert "enrollment" in response.lower() or "registr" in response.lower(), \
        "Should show enrollment information"
    print("✓ PASSED: Enrollment process shown")


def test_required_documents():
    """Test: Bot should list required documents when asked."""
    print("\n" + "="*70)
    print("TEST: REQUIRED DOCUMENTS INTENT")
    print("="*70)
    response = get_bot_response("what documents are required?")
    print(response)
    assert "documents required" in response.lower() or "documents" in response.lower(), \
        "Should mention documents"
    assert "1." in response and "10th" in response, "Should return numbered list of docs"
    print("✓ PASSED: Required documents response")


def test_long_conversation():
    """Test: the bot should continue responding even after many messages and history capped."""
    print("\n" + "="*70)
    print("TEST: LONG CONVERSATION (20+ MESSAGES)")
    print("="*70)
    user_id = 999
    for i in range(60):
        resp = get_bot_response(f"hello {i}", user_id)
        assert resp is not None and resp.strip() != "", f"Empty reply on iteration {i}"
    # verify history cap
    ctx = get_user_context(user_id)
    print(f"history length after 60 messages: {len(ctx.conversation_history)}")
    assert len(ctx.conversation_history) <= 50, "History should be capped at 50 entries"
    print("✓ PASSED: Bot still replies after 60 messages and history capped")


def test_context_tracking():
    """Test: Context management for selected college."""
    print("\n" + "="*70)
    print("TEST: CONTEXT MANAGEMENT")
    print("="*70)
    
    user_id = 123
    
    # First query - select a college
    response1 = get_bot_response("tell me about Eluru college", user_id)
    print("Query 1:", response1[:100] + "...")
    
    # Get context
    context = get_user_context(user_id)
    selected = context.get_selected_college()
    print(f"Selected College: {selected['name'] if selected else 'None'}")
    assert selected and "Eluru" in selected['name'], "Should have selected Eluru college"
    
    # Second query - use context
    response2 = get_bot_response("what about CSE fees", user_id)
    print("Query 2:", response2[:100] + "...")
    assert "Eluru" in response2 or "CSE" in response2, "Should use context from previous query"
    
    print("✓ PASSED: Context tracking working")


def run_all_tests():
    """Run all test cases."""
    print("\n\n")
    print("█████████████████████████████████████████████████████████████████")
    print("  ENHANCED CHATBOT V3 - COMPREHENSIVE TEST SUITE")
    print("█████████████████████████████████████████████████████████████████")
    
    test_list_colleges()
    test_college_details()
    test_branch_wise_fees()
    test_semester_wise_fees()
    test_deadline_dates()
    test_late_fee_penalties()
    test_unavailable_college()
    test_specific_course_in_college()
    test_enrollment_process()
    test_required_documents()
    test_long_conversation()
    test_context_tracking()
    
    print("\n\n")
    print("█████████████████████████████████████████████████████████████████")
    print("  ✓ ALL TESTS PASSED!")
    print("█████████████████████████████████████████████████████████████████")
    print("\nAll 8 user requirements have been successfully implemented:")
    print("1. ✓ College list in point-wise numbered order")
    print("2. ✓ College details first (about, placement, environment)")
    print("3. ✓ Answer specific user questions in context")
    print("4. ✓ Show unavailable message for non-trained colleges")
    print("5. ✓ Deadline dates shown according to college policies")
    print("6. ✓ Late fee penalties shown for specific college")
    print("7. ✓ Enrollment fees for different branches in order")
    print("8. ✓ Semester-wise fees according to branch")
    print("\n")


if __name__ == "__main__":
    run_all_tests()
