from django import forms

COUNTRY_CODE_CHOICES = [
    ('91', 'India (+91)'),
    ('1', 'US (+1)'),
]

LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Hindi', 'Hindi'),
    ('Kannada', 'Kannada'),
    ('Tamil', 'Tamil'),
    ('Telugu', 'Telugu'),
]

CAREGIVER_RELATIONSHIP_CHOICES = [
    ('', 'Select relationship'),
    ('Spouse', 'Spouse'),
    ('Son', 'Son'),
    ('Daughter', 'Daughter'),
    ('Parent', 'Parent'),
    ('Sibling', 'Sibling'),
    ('Friend', 'Friend'),
    ('Other', 'Other'),
]

DOCTOR_CHOICES = [
    ('Choose doctor', 'Choose doctor'),
    ('Dr. Payal Shah', 'Dr. Payal Shah'),
    ('Dr. Test', 'Dr. Test'),
]

STAFF_CHOICES = [
    ('Choose staff', 'Choose staff'),
    ('Staff Member', 'Staff Member'),
    ('Staff Test', 'Staff Test'),  # maps to 917980601033
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

DR_GRADE_CHOICES = [
    ('Not assessed', 'Not assessed'),
    ('No DR', 'No DR'),
    ('Mild NPDR', 'Mild NPDR'),
    ('Moderate NPDR', 'Moderate NPDR'),
    ('Severe NPDR', 'Severe NPDR'),
    ('PDR', 'PDR (Proliferative)'),
]

DIABETES_DURATION_CHOICES = [
    ('Unknown', 'Unknown'),
    ('Not diabetic', 'Not diabetic'),
    ('<2 years', '<2 years'),
    ('2-5 years', '2-5 years'),
    ('6-10 years', '6-10 years'),
    ('10-20 years', '10-20 years'),
    ('>20 years', '>20 years'),
]

LOCATION_CHOICES = [
    ('Select', 'Select Location'),
    ('Bangalore', 'Bangalore'),
    ('Coimbatore Sathy Road', 'Coimbatore Sathy Road'),
    ('RS Puram', 'RS Puram'),
    ('Guntur', 'Guntur'),
    ('Shimoga', 'Shimoga'),
    ('Jaipur', 'Jaipur'),
    ('Indore', 'Indore'),
    ('Panvel', 'Panvel'),
    ('Krishnankoil', 'Krishnankoil'),
    ('Anand', 'Anand'),
    ('Ludhiana', 'Ludhiana'),
    ('Kanpur', 'Kanpur'),
    ('Hyderabad', 'Hyderabad'),
    ('Varanasi', 'Varanasi'),
]

class UserRegistrationForm(forms.Form):
    full_name = forms.CharField(label="Full Name", max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    mr_no = forms.CharField(
        label="MR No.",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. SEHPAT-123456-26', 'class': 'form-control'})
    )
    patient_id = forms.CharField(
        label="Patient ID",
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 12345', 'class': 'form-control'})
    )
    country_code = forms.ChoiceField(
        label="Country Code",
        choices=COUNTRY_CODE_CHOICES,
        initial='91',
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 140px; display: inline-block;'})
    )
    phone_number = forms.CharField(
        label="Phone Number (Whatsapp)", 
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'XXXXXXXXXX',
            'maxlength': '15',
        })
    )
    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES, required=True)
    language = forms.ChoiceField(label="Preferred Language", choices=LANGUAGE_CHOICES, required=True)
    doctor_name = forms.ChoiceField(label="Doctor Assigned", choices=DOCTOR_CHOICES, required=True)
    staff_name = forms.ChoiceField(label="Staff Assigned", choices=STAFF_CHOICES, required=True)
    location = forms.ChoiceField(label="Location", choices=LOCATION_CHOICES, required=True)
    follow_up_date = forms.DateField(
        label="Follow-up Date",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    surgery_date = forms.DateField(
        label="Surgery Date (Optional)",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    dr_grade = forms.ChoiceField(
        label="DR Grade (Optional)",
        choices=DR_GRADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    diabetes_duration = forms.ChoiceField(
        label="Diabetes Duration (Optional)",
        choices=DIABETES_DURATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Caregiver (+1) — optional, encouraged
    caregiver_relationship = forms.ChoiceField(label="Caregiver Relationship", choices=CAREGIVER_RELATIONSHIP_CHOICES,
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    caregiver_phone = forms.CharField(label="Caregiver WhatsApp Number (Optional)", max_length=15, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'XXXXXXXXXX', 'class': 'form-control'}))
    caregiver_language = forms.ChoiceField(label="Caregiver Preferred Language", choices=LANGUAGE_CHOICES,
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    # consent = forms.ChoiceField(label="Consents?", choices=CONSENT_CHOICES, widget=forms.RadioSelect, required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].widget.attrs['class'] = 'form-control phone-input'

    def _clean_date_field(self, field_name):
        """Parse dd/mm/yyyy string to date object"""
        val = self.cleaned_data.get(field_name, '').strip()
        if not val:
            return None
        import re
        from datetime import date
        m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', val)
        if not m:
            raise forms.ValidationError("Date must be in dd/mm/yyyy format")
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(year, month, day)
        except ValueError:
            raise forms.ValidationError("Invalid date")

    def clean_follow_up_date(self):
        return self.cleaned_data.get('follow_up_date')  # already a date from DateField

    def clean_surgery_date(self):
        return self.cleaned_data.get('surgery_date')  # already a date from DateField

    def clean_caregiver_phone(self):
        return normalize_indian_phone(self.cleaned_data.get('caregiver_phone'), required=False)

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location == 'Select':
            raise forms.ValidationError("Please select a location")
        return location
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        country_code = self.cleaned_data.get('country_code', '91')
        # Remove any spaces, dashes, or parentheses
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if not already present
        if country_code == '91':
            if len(phone_number) == 10:
                phone_number = '91' + phone_number
            elif len(phone_number) == 12 and phone_number.startswith('91'):
                pass
            else:
                raise forms.ValidationError("Please enter a valid 10-digit Indian phone number")
        elif country_code == '1':
            if len(phone_number) == 10:
                phone_number = '1' + phone_number
            elif len(phone_number) == 11 and phone_number.startswith('1'):
                pass
            else:
                raise forms.ValidationError("Please enter a valid 10-digit US phone number")
        else:
            phone_number = country_code + phone_number
        
        return phone_number

    def clean_patient_id(self):
        pid = self.cleaned_data.get('patient_id', '').strip()
        if not pid.isdigit() or len(pid) > 5:
            raise forms.ValidationError("Patient ID must be up to 5 digits (e.g. 12345)")
        return pid

    def clean_mr_no(self):
        mid = self.cleaned_data.get('mr_no', '').strip()
        if not mid:
            return ''
        import re
        if not re.match(r'^[A-Za-z]{3,6}-[0-9]{4,6}-[0-9]{2}$', mid):
            raise forms.ValidationError("MR No. format: SEHPAT-123456-26 (letters-digits-digits)")
        return mid.upper()


# ---------------------------------------------------------------------------
# Study 1 (PHC / Adoption) forms
# ---------------------------------------------------------------------------

PHC_LOCATION_CHOICES = [
    ('Select', 'Select PHC'),
    ('Hagadur', 'Hagadur'),
    ('Siddapur', 'Siddapur'),
]

ARM_CHOICES = [
    ('Select', 'Select Track'),
    ('ai', 'AI Track'),
    ('nai', 'Non-AI Track'),
]

RELATIONSHIP_CHOICES = [
    ('', 'Select relationship'),
    ('Spouse', 'Spouse'),
    ('Son', 'Son'),
    ('Daughter', 'Daughter'),
    ('Parent', 'Parent'),
    ('Sibling', 'Sibling'),
    ('Friend', 'Friend'),
    ('Other', 'Other'),
]

STAFF_ROLE_CHOICES = [
    ('Select', 'Select role'),
    ('doctor', 'Doctor Test'),
    ('counselor', 'Staff Test'),
]


def normalize_indian_phone(raw, required=True):
    """Return a 91-prefixed 12-digit Indian number, or '' if blank & optional."""
    digits = ''.join(filter(str.isdigit, raw or ''))
    if not digits:
        if required:
            raise forms.ValidationError("Phone number is required")
        return ''
    if len(digits) == 10:
        return '91' + digits
    if len(digits) == 12 and digits.startswith('91'):
        return digits
    raise forms.ValidationError("Enter a valid 10-digit Indian phone number")


class PHCPatientForm(forms.Form):
    """PHC (adoption) patient + optional caregiver + study arm."""
    # Patient
    full_name = forms.CharField(label="Patient Name", max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    age = forms.IntegerField(label="Age", required=True, min_value=1, max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES, required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label="Patient WhatsApp Number", max_length=15, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'XXXXXXXXXX', 'class': 'form-control'}))
    language = forms.ChoiceField(label="Patient Preferred Language", choices=LANGUAGE_CHOICES, required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))
    phc_location = forms.ChoiceField(label="PHC Location", choices=PHC_LOCATION_CHOICES, required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))
    arm = forms.ChoiceField(label="Study Track", choices=ARM_CHOICES, required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))

    # Caregiver (+1) — optional but encouraged
    caregiver_relationship = forms.ChoiceField(label="Caregiver Relationship", choices=RELATIONSHIP_CHOICES,
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    caregiver_phone = forms.CharField(label="Caregiver WhatsApp Number (Optional)", max_length=15, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'XXXXXXXXXX', 'class': 'form-control'}))
    caregiver_language = forms.ChoiceField(label="Caregiver Preferred Language", choices=LANGUAGE_CHOICES,
        required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_phc_location(self):
        v = self.cleaned_data.get('phc_location')
        if v == 'Select':
            raise forms.ValidationError("Please select a PHC")
        return v

    def clean_arm(self):
        v = self.cleaned_data.get('arm')
        if v == 'Select':
            raise forms.ValidationError("Please select a study track")
        return v

    def clean_gender(self):
        v = self.cleaned_data.get('gender')
        if v == 'Select':
            raise forms.ValidationError("Please select gender")
        return v

    def clean_phone_number(self):
        return normalize_indian_phone(self.cleaned_data.get('phone_number'), required=True)

    def clean_caregiver_phone(self):
        return normalize_indian_phone(self.cleaned_data.get('caregiver_phone'), required=False)

    def clean(self):
        cleaned = super().clean()
        cg_phone = cleaned.get('caregiver_phone')
        if cg_phone:
            # If a caregiver number is given, relationship is required
            if not cleaned.get('caregiver_relationship'):
                self.add_error('caregiver_relationship', "Select the caregiver's relationship")
            if cg_phone == cleaned.get('phone_number'):
                self.add_error('caregiver_phone', "Caregiver number must differ from the patient's")
        return cleaned


class StaffForm(forms.Form):
    """Onboard a doctor or counselor (registered permanently)."""
    staff_role = forms.ChoiceField(label="Staff Role", choices=STAFF_ROLE_CHOICES, required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_staff_role(self):
        v = self.cleaned_data.get('staff_role')
        if v == 'Select':
            raise forms.ValidationError("Please select a role")
        return v


DELETE_USER_TYPE_CHOICES = [
    ('Select', 'Select user type'),
    ('patient', 'Patient / Caregiver'),
    ('doctor', 'Doctor'),
    ('counselor', 'Counselor'),
]


class DeleteUserForm(forms.Form):
    """Delete any user (patient/caregiver/doctor/counselor) by WhatsApp number."""
    phone_number = forms.CharField(label="WhatsApp Number", max_length=15, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'XXXXXXXXXX', 'class': 'form-control'}))
    user_type = forms.ChoiceField(label="User Type", choices=DELETE_USER_TYPE_CHOICES, required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_user_type(self):
        v = self.cleaned_data.get('user_type')
        if v == 'Select':
            raise forms.ValidationError("Please select a user type")
        return v

    def clean_phone_number(self):
        return normalize_indian_phone(self.cleaned_data.get('phone_number'), required=True)


