from django.shortcuts import render
from .forms import UserRegistrationForm
import requests
import json

LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
}

def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Get form data
            full_name = form.cleaned_data["full_name"]
            patient_id = form.cleaned_data["patient_id"]
            phone_number = form.cleaned_data["phone_number"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            gender = form.cleaned_data["gender"]
            language = form.cleaned_data["language"]
            doctor_name = form.cleaned_data["doctor_name"]
            staff_name = form.cleaned_data["staff_name"]
            
            # Map doctor names to phone numbers
            if doctor_name == "Dr Shirley":
                doctor_number = "919969557231"
            elif doctor_name == "Dr Salma":
                doctor_number = "917034432034"
            elif doctor_name == "Dr Umesh":
                doctor_number = "918700105161"
            else:
                doctor_number = "919739811075"  # Default

            if staff_name == "Dr Shubha Nayak":
                staff_number = "917022488975"
            # elif staff_name == "Dr Salma":
            #     staff_number = "917034432034"
            # elif staff_name == "Dr Umesh":
            #     staff_number = "918700105161"
            else:
                staff_number = "919739811075"  # Default

            # Map language to code
            language_code = LANGUAGE_CODES.get(language, "en")
            
            # Calculate age if date of birth is provided
            age = None
            dob_str = None
            if date_of_birth:
                from datetime import date
                today = date.today()
                age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
                dob_str = date_of_birth.strftime("%Y-%m-%d")

            # Create new API body structure
            api_body = json.dumps([{
                "phone_number_id": phone_number,
                "user_id": patient_id,
                "user_name": full_name,
                "user_language": language_code,
                "user_type": "byoebuser",
                "patient_details": {
                    "date_of_birth": dob_str,
                    "gender": gender,
                    "age": age,
                },
                "experts": {
                    "byoebexpert": [doctor_number], 
                    "byoebexpert2": [staff_number]
                }
            }])

            # print()
            print(api_body)

            try:
                response = requests.post(
                    "https://oncobot-h7fme6hue9f7buds.canadacentral-01.azurewebsites.net/register_users",
                    # "http://localhost:5000/register_users",
                    headers={"Content-Type": "application/json"},
                    data=api_body
                )
                if response.status_code == 200:
                    return render(request, "registration_app/registration_success.html")
                else:
                    return render(request, "registration_app/registration_form.html", {"form": form, "error": f"API Error: {response.status_code}"})
            except Exception as e:
                return render(request, "registration_app/registration_form.html", {"form": form, "error": str(e)})

    else:
        form = UserRegistrationForm()

    return render(request, "registration_app/registration_form.html", {"form": form})
