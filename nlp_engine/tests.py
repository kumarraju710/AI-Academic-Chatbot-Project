from django.test import TestCase
# the UI and most of the application now use the deterministic engine in
# ``services_new``; tests continue to exercise the old module as well, but
# the underlying implementation is the same after our refactor above.

from .chatbot import get_chatbot_response, colleges_data, faq_data
from .services_new import generate_response as generate_response_new


from django.contrib.auth import get_user_model

User = get_user_model()


class ChatbotLogicTests(TestCase):
    def setUp(self):
        # create a user for view tests
        self.user = User.objects.create_user(username='tester', password='secret')

    def test_list_colleges(self):
        msg = "Please list colleges"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertIn("These are the Available Colleges to give the information", resp)
        self.assertIn("Aditya College of Engineering", resp)
        self.assertIn("Pragati Engineering College", resp)

    def test_list_colleges_variants(self):
        for msg in ["show colleges", "college list", "jntuk colleges", "list of colleges"]:
            resp = get_chatbot_response(msg, colleges_data, faq_data)
            self.assertIn("Available Colleges under JNTUK", resp)

    def test_university_without_college_keyword(self):
        # should not return list when only 'university' is mentioned
        msg = "Tell me about the university"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertNotIn("Available Colleges under JNTUK", resp)
        self.assertTrue(resp)

    def test_keyword_abbreviation_match(self):
        # abbreviated college names from the keywords dataset should work
        for kw in ["gmrit", "vsm", "giet", "pragati", "aditya"]:
            msg = f"{kw} fee"
            resp = get_chatbot_response(msg, colleges_data, faq_data)
            self.assertNotIn("Available Colleges under JNTUK", resp)
            self.assertIn("Fee", resp)

    def test_paid_not_misclassified_as_ai(self):
        # ensure the substring 'ai' inside another word doesn't trigger a match
        msg = "Have you paid the fees?"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        # the reply should be generic or unrelated, not a college detail
        self.assertNotIn("College:", resp)


    def test_specific_college_override_list(self):
        # when a specific college is mentioned alongside generic keywords,
        # we must still return details for that college
        msg = "i want to know about vsm college"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertFalse(resp.startswith("Available Colleges under JNTUK"))
        self.assertIn("College: VSM College of Engineering", resp)

    def test_vsm_course_fee(self):
        msg = "vsm college cse fee"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertIn("VSM College of Engineering – CSE Fee", resp)
        self.assertNotIn("Available Colleges under JNTUK", resp)

    def test_specific_college_details(self):
        msg = "Aditya fees"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertTrue(resp.startswith("College: Aditya College of Engineering"))
        self.assertIn("Location: Surampalem", resp)
        self.assertIn("Courses & Fees", resp)
        self.assertIn("Deadline: July 31", resp)

    def test_college_not_available(self):
        msg = "XYZ college fees"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertIn("currently unavailable", resp)

    def test_fee_structure_for_college(self):
        msg = "fee structure Pragati"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertIn("Fee structure for Pragati Engineering College", resp)
        self.assertIn("1. CSE – ₹55,000 per year", resp)

    def test_specific_course_fee(self):
        msg = "Aditya CSE fee"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertIn("Aditya College of Engineering – CSE Fee: ₹55,000 per year", resp)
        self.assertIn("Deadline: July 31", resp)

    def test_semester_fee_calculation(self):
        msg = "What is the semester fee for GMR CSE?"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertIn("Per semester", resp)
        self.assertIn("₹54,000", resp)  # 108000/2

    def test_semester_fee_general(self):
        msg = "semester fee Aditya"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertIn("Semester-wise fees", resp)
        self.assertIn("Annual ₹55,000", resp)
        self.assertIn("Semester ₹27,500", resp)

    def test_generic_intent_response(self):
        msg = "hello"
        resp = get_chatbot_response(msg, colleges_data, faq_data)
        self.assertNotEqual(resp, "")
        self.assertIn("Hello", resp)

    # integration checks
    def test_generate_response_matches_structured(self):
        # both the old ``services`` module and the new deterministic service
        # should return identical responses
        from .services import generate_response as legacy_generate

        msg = "Aditya fees"
        r1 = legacy_generate(msg)
        r2 = get_chatbot_response(msg, colleges_data, faq_data)
        r3 = generate_response_new(msg)
        self.assertEqual(r1, r2)
        self.assertEqual(r2, r3)

    def test_ask_question_view(self):
        self.client.login(username='tester', password='secret')
        response = self.client.get('/chatbot/ask_question', {'q': 'Aditya fees'})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('reply', body)
        self.assertIn('Aditya College of Engineering', body['reply'])
