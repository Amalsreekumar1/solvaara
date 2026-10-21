import re

from django import forms

from .models import Enquiry

INPUT = (
    "w-full px-4 py-3 bg-surface-container-low text-on-surface "
    "placeholder:text-outline focus:bg-surface-container-lowest "
    "focus:outline-none focus:ring-1 focus:ring-secondary transition-colors"
)


class EnquiryForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        label="Leave this empty",
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    class Meta:
        model = Enquiry
        fields = ["customer_name", "email", "phone", "message"]
        labels = {
            "customer_name": "Full name",
            "email": "Email address",
            "phone": "Phone or WhatsApp (optional)",
            "message": "Your message",
        }
        widgets = {
            "customer_name": forms.TextInput(
                attrs={"class": INPUT, "autocomplete": "name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": INPUT, "autocomplete": "email"}
            ),
            "phone": forms.TextInput(
                attrs={"class": INPUT, "autocomplete": "tel", "inputmode": "tel"}
            ),
            "message": forms.Textarea(attrs={"class": INPUT, "rows": 5}),
        }

    def clean_customer_name(self):
        name = self.cleaned_data["customer_name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your name.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if phone and not re.fullmatch(r"[0-9+()\-\s]{7,20}", phone):
            raise forms.ValidationError(
                "Enter a valid phone number, for example +91 98765 43210."
            )
        return phone

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("Please write at least a short sentence.")
        return message

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam check failed.")
        return ""