from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from rest_framework.decorators import api_view
import threading
import speech_recognition as sr

# Global flag to control speech recognition
is_running = False
recognizer = sr.Recognizer()

# Define threat words
THREAT_WORDS = ["help", "help me", "stop", "danger", "fire", "police", "please"]

def recognize_speech():
    global is_running
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while is_running:
            try:
                print("Listening... Speak now:")
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio).lower()
                print("You said:", text)

                if any(word in text for word in THREAT_WORDS):
                    print("ALERT: Threat detected! 🚨")
                    trigger_alert(text)
                else:
                    print("No threat detected.")

            except sr.UnknownValueError:
                print("Sorry, I couldn't understand the audio.")
            except sr.RequestError:
                print("Error connecting to the speech recognition service.")

def trigger_alert(detected_text):
    print(f"ALERT TRIGGERED: Detected threat phrase -> '{detected_text}'")

def start_recognition():
    global is_running
    if not is_running:
        is_running = True
        thread = threading.Thread(target=recognize_speech)
        thread.daemon = True
        thread.start()
        return {"message": "Speech recognition started."}
    return {"message": "Already running."}

def stop_recognition():
    global is_running
    is_running = False
    return {"message": "Speech recognition stopped."}

@api_view(['GET'])
def start(request):
    return JsonResponse(start_recognition())

@api_view(['GET'])
def stop(request):
    return JsonResponse(stop_recognition())

@api_view(['GET'])
def status(request):
    return JsonResponse({"running": is_running})
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import EmergencyContact
from twilio.rest import Client
import requests
from geopy.geocoders import Nominatim

TWILIO_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_NUMBER = settings.TWILIO_PHONE_NUMBER

client = Client(TWILIO_SID, TWILIO_TOKEN)

# Function to get live location (Mock API or GPS Data)
def get_live_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        location = data.get("loc", "")
        return f"https://www.google.com/maps?q={location}"
    except:
        return "Location not available"

# 1️⃣ Add Emergency Contact
@api_view(['POST'])
def add_contact(request):
    name = request.data.get("name")
    phone = request.data.get("phone_number")
    contact = EmergencyContact.objects.create(name=name, phone_number=phone)
    return Response({"message": "Contact added successfully"}, status=201)

# 2️⃣ SOS Emergency Alert (Calls & SMS)
@api_view(['POST'])
def sos_alert(request):
    emergency_msg = "🚨 SOS Alert! I am in danger! Here is my live location: " + get_live_location()
    
    # Call Police (Simulated)
    print("Calling Police at 112...")

    # Send SMS to Family
    contacts = EmergencyContact.objects.all()
    for contact in contacts:
        client.messages.create(
            body=emergency_msg,
            from_=TWILIO_NUMBER,
            to=contact.phone_number
        )

    return Response({"message": "SOS Alert sent!"}, status=200)

# 3️⃣ Detect Danger Zone & Auto-Send Alert
@api_view(['POST'])
def danger_zone_check(request):
    user_lat = request.data.get("latitude")
    user_lon = request.data.get("longitude")
    
    # Hardcoded Danger Zones (Modify as needed)
    DANGER_ZONES = [(18.5204, 73.8567), (28.7041, 77.1025)]  

    for danger_lat, danger_lon in DANGER_ZONES:
        if abs(user_lat - danger_lat) < 0.01 and abs(user_lon - danger_lon) < 0.01:
            sos_alert(request)
            return Response({"message": "Entered Danger Zone! Alert Sent!"}, status=200)
    
    return Response({"message": "Safe Zone"}, status=200)
