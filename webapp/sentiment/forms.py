from django import forms

class TextInputForm(forms.Form):
    textInput = forms.CharField(widget=forms.Textarea(
        attrs={
            'class':'form-control',
            'id':'textInput_id',
            'required':True,
            'placeholder': 'Eg. Best foods in town',
            'rows': 5,
        }
    ))
    