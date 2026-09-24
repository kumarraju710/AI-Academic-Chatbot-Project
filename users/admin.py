from django.contrib import admin
from django import forms
import json
from .models import User, FAQ, ChatLog, Feedback


class FAQAdminForm(forms.ModelForm):
    answer_list = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter answers separated by new lines. Each line will be an item in the JSON list."
    )

    class Meta:
        model = FAQ
        fields = ['intent', 'question', 'answer_list']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Load existing answers
            answers = self.instance.answer or []
            self.fields['answer_list'].initial = '\n'.join(answers)

    def clean_answer_list(self):
        data = self.cleaned_data['answer_list']
        # Split by lines and strip
        answers = [line.strip() for line in data.split('\n') if line.strip()]
        if not answers:
            raise forms.ValidationError("At least one answer is required.")
        return answers

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.answer = self.cleaned_data['answer_list']
        if commit:
            instance.save()
        return instance


class FAQAdmin(admin.ModelAdmin):
    form = FAQAdminForm
    list_display = ['intent', 'question']


admin.site.register(User)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(ChatLog)
admin.site.register(Feedback)
