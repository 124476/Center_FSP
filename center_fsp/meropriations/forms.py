from django import forms
from django.utils.translation import gettext_lazy as _

from meropriations.models import Meropriation, Result, Structure, Tip, Discipline
from users.models import Region


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if len(self.visible_fields()) == 1:
            self.visible_fields()[0].field.widget.attrs[
                "class"
            ] = "form-control input-field-only-one"
        else:
            for field in self.visible_fields():
                field.field.widget.attrs["class"] = "form-control input-field"
                if isinstance(field.field.widget, forms.CheckboxInput):
                    field.field.widget.attrs["class"] = "form-check-input"

        self.update_errors_class()

    def update_errors_class(self):
        for field in self.visible_fields():
            if self.errors.get(field.name):
                if "is-invalid" not in field.field.widget.attrs["class"]:
                    field.field.widget.attrs["class"] += " is-invalid"

    def add_error(self, field, error):
        super().add_error(field, error)
        self.update_errors_class()


class MeropriationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Meropriation
        fields = [
            "name", "text", "count", "place", "structure",
            "tip", "disciplines", "date_start", "date_end"
        ]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "cols": 40}),
            "place": forms.Textarea(attrs={"rows": 4, "cols": 40}),
            "date_start": forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}),
            "date_end": forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}),
        }

    disciplines = forms.ModelMultipleChoiceField(
        queryset=Discipline.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-control select-multiple-discipline"}),
        required=True,
        label="Выбор дисциплин"
    )

    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        if date_start and date_end and date_end < date_start:
            raise forms.ValidationError(
                _("The end date must be after the start date.")
            )

        return cleaned_data


class ResultForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = Result
        fields = ['meropriation', 'file']

