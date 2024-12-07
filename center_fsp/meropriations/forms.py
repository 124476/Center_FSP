from django import forms

from meropriations.models import Meropriation, Result, Structure, Tip
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
            "name", "text", "count", "place", "normal_place", "structure",
            "tip", "disciplines", "date_start", "date_end"
        ]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "cols": 40}),
            "place": forms.Select(attrs={"class": "form-control"}),
            "normal_place": forms.Textarea(attrs={"rows": 2}),
            "date_start": forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}),
            "date_end": forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}),
        }

    place = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Место проведения"
    )


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiFileUploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Result

        fields = (Result.file.field.name,)
        labels = {
            Result.file.field.name: "Загрузить файлы",
        }
        help_texts = {
            Result.file.field.name: "Загрузка файлы",
        }
        widgets = {
            Result.file.field.name: MultipleFileInput(
                attrs={
                    "multiple": True,
                },
            ),
        }


class MeropriationStatusForm(forms.ModelForm):
    class Meta:
        model = Meropriation
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }


__all__ = ()
