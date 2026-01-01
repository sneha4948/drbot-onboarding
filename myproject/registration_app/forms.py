from django import forms

LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Hindi', 'Hindi'),
    ('Kannada', 'Kannada'),
    ('Tamil', 'Tamil'),
    ('Telugu', 'Telugu'),
]

DOCTOR_CHOICES = [
    ('Choose doctor', 'Choose doctor'),
    ('Dr. Payal Shah', 'Dr. Payal Shah'),
    ('Dr. Test', 'Dr. Test'),
]

STAFF_CHOICES = [
    ('Choose staff', 'Choose staff'),
    ('Staff Member', 'Staff Member'),
    ('Staff Test', 'Staff Test'),
]

CONSENT_CHOICES = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]

GENDER_CHOICES = [
    ('Select', 'Select'),
    ('Male', 'Male'),
    ('Female', 'Female'),
]

class UserRegistrationForm(forms.Form):
    full_name = forms.CharField(label="Full Name", max_length=100, required=True)
    patient_id = forms.CharField(label="Patient ID", max_length=100, required=True)
    phone_number = forms.CharField(
        label="Phone Number (Whatsapp)", 
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'XXXXXXXXXX',
            'maxlength': '10',
        })
    )
    # email = forms.EmailField(label="Email Address", required=False)
    date_of_birth = forms.DateField(
        label="Date of Birth (mm/dd/yyyy)", 
        widget=forms.DateInput(attrs={'type': 'date'}), 
        required=False
    )
    # age = forms.IntegerField(label="Age", required=False)
    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES, required=True)
    language = forms.ChoiceField(label="Preferred Language", choices=LANGUAGE_CHOICES, required=True)
    doctor_name = forms.ChoiceField(label="Doctor Assigned", choices=DOCTOR_CHOICES, required=True)
    staff_name = forms.ChoiceField(label="Staff Assigned", choices=STAFF_CHOICES, required=True)
    # consent = forms.ChoiceField(label="Consents?", choices=CONSENT_CHOICES, widget=forms.RadioSelect, required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        self.fields['phone_number'].widget.attrs['class'] = 'form-control phone-input'
        self.fields['date_of_birth'].widget.attrs['class'] = 'form-control'
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        # Remove any spaces, dashes, or parentheses
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # If user entered number without country code, assume it's Indian
        if len(phone_number) == 10:
            phone_number = '91' + phone_number
        elif len(phone_number) == 12 and phone_number.startswith('91'):
            pass  # Already has country code
        else:
            raise forms.ValidationError("Please enter a valid Indian phone number")
        
        return phone_number
