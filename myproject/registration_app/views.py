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
            mr_no = form.cleaned_data.get("mr_no", "")
            phone_number = form.cleaned_data["phone_number"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            gender = form.cleaned_data["gender"]
            language = form.cleaned_data["language"]
            doctor_name = form.cleaned_data["doctor_name"]
            staff_name = form.cleaned_data["staff_name"]
            location = form.cleaned_data.get("location", "")
            follow_up_date = form.cleaned_data.get("follow_up_date")
            surgery_date = form.cleaned_data.get("surgery_date")
            dr_grade = form.cleaned_data.get("dr_grade", "Not assessed")
            diabetes_duration = form.cleaned_data.get("diabetes_duration", "Unknown")
            
            # Map doctor names to phone numbers
            if doctor_name == "Dr. Payal Shah":
                doctor_number = "918088506150"
            elif doctor_name == "Dr. Test":
                doctor_number = "919353935536"  # Test Doctor (your number)
            else:
                doctor_number = "918088506150"  # Default to Dr. Payal Shah

            if staff_name == "Staff Member":
                staff_number = "918667406490"
            elif staff_name == "Staff Test":
                # staff_number = "919999999999"  # old test number
                staff_number = "917980601033"  # Shimoga counsellor
            else:
                staff_number = "918667406490"  # Default

            # Map location to org_id for location-specific KB
            LOCATION_TO_ORG = {
                "Shimoga": "SMG",
                "Bangalore": "BLR",
                "Hyderabad": "HYD",
                "Jaipur": "JAI",
                "Coimbatore Sathy Road": "CBE",
                "RS Puram": "RSP",
                "Guntur": "GNT",
                "Indore": "IDR",
                "Panvel": "PNV",
                "Krishnankoil": "KNK",
                "Anand": "AND",
                "Ludhiana": "LDH",
                "Kanpur": "KNP",
                "Varanasi": "VNS",
            }
            org_id = LOCATION_TO_ORG.get(location, "drbot")

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

            # Format dates for API
            follow_up_str = follow_up_date.strftime("%Y-%m-%d") if follow_up_date else None
            surgery_str = surgery_date.strftime("%Y-%m-%d") if surgery_date else None

            # Build user_location — only include filled optional fields
            user_location = {
                "is_onboarded": False,
                "registered_from_webapp": True,
                "org_id": org_id,
                "location": location,
            }
            if mr_no:
                user_location["mr_no"] = mr_no
            if gender and gender != "Select":
                user_location["gender"] = gender
            if dob_str:
                user_location["dob"] = dob_str
            if dr_grade and dr_grade != "Not assessed":
                user_location["dr_grade"] = dr_grade
            if diabetes_duration and diabetes_duration != "Unknown":
                user_location["diabetes_duration"] = diabetes_duration
            if follow_up_str:
                user_location["follow_up_date"] = follow_up_str
            if surgery_str:
                user_location["surgery_date"] = surgery_str

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
                "user_location": user_location
            }])

            # print()
            print(api_body)

            try:
                response = requests.post(
                    "https://drbot-app-dbgeh8gzbtdtbyb0.canadacentral-01.azurewebsites.net/register_users",  # Azure production
                    # "http://127.0.0.1:5000/register_users",  # local testing
                    headers={"Content-Type": "application/json"},
                    data=api_body
                )
                if response.status_code == 200:
                    # Check if user was already registered
                    response_data = response.json()
                    
                    # Handle both response formats (dict or list)
                    is_already_registered = False
                    if isinstance(response_data, dict):
                        messages = response_data.get("message", [])
                        if isinstance(messages, list):
                            is_already_registered = any("Already registered" in msg.get("message", "") 
                                                        for msg in messages if isinstance(msg, dict))
                    elif isinstance(response_data, list):
                        is_already_registered = any("Already registered" in item.get("message", "") 
                                                    for item in response_data if isinstance(item, dict))
                    
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
