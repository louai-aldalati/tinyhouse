from django import forms

class ReservationDatesForm(forms.Form):
    start_date = forms.DateField(input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(input_formats=['%Y-%m-%d'])

    def clean(self):
        cleaned = super().clean()
        sd = cleaned.get('start_date')
        ed = cleaned.get('end_date')
        if sd and ed and sd >= ed:
            raise forms.ValidationError('Çıkış Tarihi, Giriş Tarihinden Sonra Olmalıdır.')
        return cleaned
