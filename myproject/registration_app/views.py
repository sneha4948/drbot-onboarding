from django.shortcuts import render
from .forms import UserRegistrationForm
import requests
import json

LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
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
            if doctor_name == "Dr. Payal Shah":
                doctor_number = "918088506150"
            elif doctor_name == "Dr. Test":
                doctor_number = "918667406490"  # Use staff member's number to avoid conflict
            else:
                doctor_number = "918088506150"  # Default to Dr. Payal Shah

            if staff_name == "Staff Member":
                staff_number = "918667406490"
            elif staff_name == "Staff Test":
                staff_number = "919999999999"  # Unique test number to avoid conflicts
            else:
                staff_number = "918667406490"  # Default to Staff Member

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
                "user_type": "drbot_user",
                "patient_details": {
                    "date_of_birth": dob_str,
                    "gender": gender,
                    "age": age,
                },
                "experts": {
                    "medical": [doctor_number], 
                    "logistical": [staff_number]
                },
                "user_location": {
                    "is_onboarded": False,
                    "registered_from_webapp": True
                }
            }])

            # print()
            print(api_body)

            try:
                response = requests.post(
                    "https://drbot-app-dbgeh8gzbtdtbyb0.canadacentral-01.azurewebsites.net/register_users",
                    headers={"Content-Type": "application/json"},
                    data=api_body
                )
                if response.status_code == 200:
                    # Check if user was already registered
                    response_data = response.json()
                    is_already_registered = any("Already registered" in msg.get("message", "") 
                                                for msg in response_data.get("message", []))
                    
                    return render(request, "registration_app/registration_success.html", {
                        "is_already_registered": is_already_registered
                    })
                else:
                    return render(request, "registration_app/registration_form.html", {"form": form, "error": f"API Error: {response.status_code}"})
            except Exception as e:
                return render(request, "registration_app/registration_form.html", {"form": form, "error": str(e)})

    else:
        form = UserRegistrationForm()

    return render(request, "registration_app/registration_form.html", {"form": form})
