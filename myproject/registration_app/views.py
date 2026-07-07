from django.shortcuts import render
from .forms import UserRegistrationForm, PHCPatientForm, StaffForm, DeleteUserForm
import requests
import json
import hashlib

LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
}

# Bot register endpoint (Azure production) and staff numbers
BOT_REGISTER_URL = "https://drbot-app-dbgeh8gzbtdtbyb0.canadacentral-01.azurewebsites.net/register_users"
BOT_DELETE_URL = "https://drbot-app-dbgeh8gzbtdtbyb0.canadacentral-01.azurewebsites.net/delete_users"
DOCTOR_TEST_NUMBER = "919353935536"
COUNSELOR_TEST_NUMBER = "917980601033"


def _md5(text):
    return hashlib.md5(text.encode()).hexdigest()

def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Get form data
            full_name = form.cleaned_data["full_name"]
            patient_id = form.cleaned_data["patient_id"]
            mr_no = form.cleaned_data.get("mr_no", "")
            phone_number = form.cleaned_data["phone_number"]
            gender = form.cleaned_data["gender"]
            language = form.cleaned_data["language"]
            doctor_name = form.cleaned_data["doctor_name"]
            staff_name = form.cleaned_data["staff_name"]
            location = form.cleaned_data.get("location", "")
            follow_up_date = form.cleaned_data.get("follow_up_date")
            surgery_date = form.cleaned_data.get("surgery_date")
            dr_grade = form.cleaned_data.get("dr_grade", "Not assessed")
            diabetes_duration = form.cleaned_data.get("diabetes_duration", "Unknown")
            caregiver_relationship = form.cleaned_data.get("caregiver_relationship", "")
            caregiver_phone = form.cleaned_data.get("caregiver_phone", "")
            caregiver_language = form.cleaned_data.get("caregiver_language", "")

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
            if dr_grade and dr_grade != "Not assessed":
                user_location["dr_grade"] = dr_grade
            if diabetes_duration and diabetes_duration != "Unknown":
                user_location["diabetes_duration"] = diabetes_duration
            if follow_up_str:
                user_location["follow_up_date"] = follow_up_str
            if surgery_str:
                user_location["surgery_date"] = surgery_str

            # Build patient (+ optional caregiver) as linked VC users (vc_ai)
            experts = {"medical": [doctor_number], "logistical": [staff_number]}
            user_location["patient_id"] = patient_id
            if caregiver_phone:
                user_location["caregiver_phone"] = caregiver_phone
            users = [{
                "phone_number_id": phone_number,
                "user_id": _md5(phone_number),
                "user_name": full_name,
                "user_language": language_code,
                "user_type": "drbot_user",
                "user_group": "vc_ai",
                "experts": experts,
                "audience": [],
                "user_location": user_location,
            }]
            if caregiver_phone:
                cg_lang = LANGUAGE_CODES.get(caregiver_language or language, "en")
                users.append({
                    "phone_number_id": caregiver_phone,
                    "user_id": _md5(caregiver_phone),
                    "user_name": f"{full_name} ({caregiver_relationship or 'Caregiver'})",
                    "user_language": cg_lang,
                    "user_type": "drbot_user",
                    "user_group": "vc_ai",
                    "experts": experts,
                    "audience": [],
                    "user_location": {
                        "is_onboarded": False,
                        "registered_from_webapp": True,
                        "org_id": org_id,
                        "location": location,
                        "is_caregiver": True,
                        "relationship": caregiver_relationship,
                        "patient_phone": phone_number,
                    },
                })
            api_body = json.dumps(users)

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


def landing(request):
    """First page: choose Patient (PHC/VC) or Staff (Doctor/Counselor)."""
    return render(request, "registration_app/landing.html")


def register_phc(request):
    """PHC (adoption) patient + optional caregiver onboarding."""
    if request.method == "POST":
        form = PHCPatientForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            arm = cd["arm"]                      # 'ai' | 'nai'
            user_group = f"phc_{arm}"            # phc_ai | phc_nai
            phc = cd["phc_location"]
            patient_phone = cd["phone_number"]
            caregiver_phone = cd.get("caregiver_phone")
            experts = {
                "medical": [DOCTOR_TEST_NUMBER],
                "logistical": [COUNSELOR_TEST_NUMBER],
            }

            users = []
            patient = {
                "phone_number_id": patient_phone,
                "user_id": _md5(patient_phone),
                "user_name": cd["full_name"],
                "user_language": LANGUAGE_CODES.get(cd["language"], "en"),
                "user_type": "drbot_user",
                "user_group": user_group,
                "experts": experts,
                "audience": [],
                "user_location": {
                    "org_id": "drbot",
                    "location": phc,
                    "age": cd["age"],
                    "gender": cd["gender"],
                    "registered_from_webapp": True,
                    "is_onboarded": False,
                },
            }
            if caregiver_phone:
                patient["user_location"]["caregiver_phone"] = caregiver_phone
            users.append(patient)

            if caregiver_phone:
                cg_lang = LANGUAGE_CODES.get(cd.get("caregiver_language") or cd["language"], "en")
                users.append({
                    "phone_number_id": caregiver_phone,
                    "user_id": _md5(caregiver_phone),
                    "user_name": f"{cd['full_name']} ({cd.get('caregiver_relationship', 'Caregiver')})",
                    "user_language": cg_lang,
                    "user_type": "drbot_user",
                    "user_group": user_group,
                    "experts": experts,
                    "audience": [],
                    "user_location": {
                        "org_id": "drbot",
                        "location": phc,
                        "registered_from_webapp": True,
                        "is_onboarded": False,
                        "is_caregiver": True,
                        "relationship": cd.get("caregiver_relationship", ""),
                        "patient_phone": patient_phone,
                    },
                })

            try:
                response = requests.post(
                    BOT_REGISTER_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(users),
                )
                if response.status_code == 200:
                    return render(request, "registration_app/registration_success.html",
                                  {"is_already_registered": False})
                return render(request, "registration_app/phc_form.html",
                              {"form": form, "error": f"API Error: {response.status_code}"})
            except Exception as e:
                return render(request, "registration_app/phc_form.html",
                              {"form": form, "error": str(e)})
    else:
        form = PHCPatientForm()
    return render(request, "registration_app/phc_form.html", {"form": form})


def register_staff(request):
    """Onboard a doctor or counselor (registered permanently)."""
    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["staff_role"]   # 'doctor' | 'counselor'
            if role == "doctor":
                phone, user_type, name = DOCTOR_TEST_NUMBER, "drbot_expert", "Dr. Test"
            else:
                phone, user_type, name = COUNSELOR_TEST_NUMBER, "drbot_expert2", "Counselor Test"
            staff = {
                "phone_number_id": phone,
                "user_id": _md5(phone),
                "user_name": name,
                "user_language": "en",
                "user_type": user_type,
                "experts": {},
                "audience": [],
                "user_location": {"registered_from_webapp": True, "is_onboarded": False},
            }
            try:
                response = requests.post(
                    BOT_REGISTER_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps([staff]),
                )
                if response.status_code == 200:
                    return render(request, "registration_app/registration_success.html",
                                  {"is_already_registered": False})
                return render(request, "registration_app/staff_form.html",
                              {"form": form, "error": f"API Error: {response.status_code}"})
            except Exception as e:
                return render(request, "registration_app/staff_form.html",
                              {"form": form, "error": str(e)})
    else:
        form = StaffForm()
    return render(request, "registration_app/staff_form.html", {"form": form})


def delete_user(request):
    """Delete any user (patient/caregiver/doctor/counselor) by WhatsApp number."""
    if request.method == "POST":
        form = DeleteUserForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            try:
                response = requests.delete(
                    BOT_DELETE_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps([phone]),
                )
                if response.status_code == 200:
                    return render(request, "registration_app/delete_form.html",
                                  {"form": DeleteUserForm(), "success": phone})
                return render(request, "registration_app/delete_form.html",
                              {"form": form, "error": f"API Error: {response.status_code}"})
            except Exception as e:
                return render(request, "registration_app/delete_form.html",
                              {"form": form, "error": str(e)})
    else:
        form = DeleteUserForm()
    return render(request, "registration_app/delete_form.html", {"form": form})

