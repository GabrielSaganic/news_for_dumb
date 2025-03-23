from django import forms
from scraper.models import Tag


class SummarizerForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget, label="Select a Date")
    tag = forms.ModelChoiceField(queryset=Tag.get_today_top_10(), label="Select a Tag")
    country = forms.ChoiceField(
        choices=[
            ("HR", "Croatia"),
            ("BA", "Bosnia and Herzegovina"),
            ("RS", "Serbia"),
        ],
        label="Select a Country",
    )
