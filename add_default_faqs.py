import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from users.models import FAQ

# Add some default FAQs
faqs = [
    {
        "intent": "fee_structure",
        "question": "What are the tuition fees?",
        "answer": ["Tuition fees are $1200 per semester for Software Engineering students."]
    },
    {
        "intent": "payment_methods",
        "question": "How can I pay the fees?",
        "answer": ["Fees can be paid online via the university portal using UPI, net banking, or credit/debit card, or offline via bank challan."]
    },
    {
        "intent": "fee_deadlines",
        "question": "When is the payment deadline?",
        "answer": ["Semester fee payment is due by April 5."]
    },
    {
        "intent": "enrollment_process",
        "question": "How to enroll?",
        "answer": ["The enrollment process begins with online registration through the university portal followed by document verification and fee payment."]
    }
]

for faq in faqs:
    if not FAQ.objects.filter(question=faq["question"]).exists():
        FAQ.objects.create(
            intent=faq["intent"],
            question=faq["question"],
            answer=json.dumps(faq["answer"])
        )

print("Default FAQs added.")