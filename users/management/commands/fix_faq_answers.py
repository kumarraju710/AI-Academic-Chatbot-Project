from django.core.management.base import BaseCommand
import json
from users.models import FAQ

class Command(BaseCommand):
    help = 'Fix FAQ answers to be valid JSON lists'

    def handle(self, *args, **options):
        for faq in FAQ.objects.all():
            if isinstance(faq.answer, str):
                # If it's a string, wrap it in a list
                faq.answer = json.dumps([faq.answer])
                faq.save()
                self.stdout.write(f'Fixed FAQ {faq.id}: {faq.question}')
            elif isinstance(faq.answer, list):
                # If it's already a list, ensure it's JSON
                faq.answer = json.dumps(faq.answer)
                faq.save()
                self.stdout.write(f'Ensured JSON for FAQ {faq.id}: {faq.question}')
            else:
                self.stdout.write(f'Skipping FAQ {faq.id}: already valid')

        self.stdout.write('All FAQs fixed.')