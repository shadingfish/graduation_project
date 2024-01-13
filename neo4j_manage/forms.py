from django import forms
from .models import Crop


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = [
            "latin_name",
            "family_name",
            "genus_name",
            "chinese_name",
            "chinese_family_name",
            "chinese_genus_name",
        ]
