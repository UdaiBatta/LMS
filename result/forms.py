from decimal import Decimal

from django import forms


class ScoreEntryForm(forms.Form):
    """Validate one student's assessment components before saving grades."""

    assignment = forms.DecimalField(min_value=0, max_value=100, decimal_places=2)
    mid_exam = forms.DecimalField(min_value=0, max_value=100, decimal_places=2)
    quiz = forms.DecimalField(min_value=0, max_value=100, decimal_places=2)
    attendance = forms.DecimalField(min_value=0, max_value=100, decimal_places=2)
    final_exam = forms.DecimalField(min_value=0, max_value=100, decimal_places=2)

    def clean(self):
        cleaned_data = super().clean()
        fields = (
            "assignment",
            "mid_exam",
            "quiz",
            "attendance",
            "final_exam",
        )
        if all(field in cleaned_data for field in fields):
            total = sum((cleaned_data[field] for field in fields), Decimal("0"))
            if total > 100:
                raise forms.ValidationError(
                    "The combined score components cannot exceed 100."
                )
        return cleaned_data
