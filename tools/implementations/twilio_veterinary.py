"""
FILE: tools/implementations/twilio_veterinary.py
PURPOSE: Twilio integration for veterinary AI phone answering and call routing

DEPENDENCIES:
- twilio ^8.0.0 (Twilio REST API client)
- config (API key management)

EXPORTS:
- twilio_vet_answer_call(to, from_, greeting_text, **kwargs) - AI-powered phone answering
- twilio_vet_route_call(call_sid, route_to, **kwargs) - Intelligent call routing
- twilio_vet_handle_voicemail(call_sid, recording_url, **kwargs) - Process voicemail
- twilio_vet_schedule_callback(phone, preferred_time, **kwargs) - Schedule callback
- twilio_vet_send_appointment_reminder(phone, appointment_details, **kwargs) - Send SMS reminder
- twilio_vet_emergency_triage(call_sid, symptoms, **kwargs) - Emergency assessment

USED BY:
- AI_infrastructure/routes/agent_routes.py (tool execution)
- veterinary practice workflows (appointment booking, emergency triage)

NOTES:
- Requires Twilio account with phone number provisioned
- Uses TwiML for call flow control
- Integrates with AssemblyAI for speech-to-text
- Supports business hours routing and emergency detection
- Cost: ~$0.04 per call minute + $0.0085 per text

LAST MODIFIED: 2025-11-25 - Initial implementation for veterinary AI phone system
"""

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class TwilioVeterinaryError(Exception):
    """Custom exception for Twilio veterinary operations"""
    pass


class TwilioVeterinaryTools:
    """Twilio integration for veterinary practice phone system"""
    
    def __init__(self, **kwargs):
        """Initialize Twilio client with credentials"""
        account_sid = kwargs.get('account_sid') or os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = kwargs.get('auth_token') or os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            raise TwilioVeterinaryError("Twilio credentials not provided")
        
        self.client = Client(account_sid, auth_token)
        self.phone_number = kwargs.get('phone_number') or os.getenv('TWILIO_PHONE_NUMBER')
        
        # Business hours (24-hour format)
        self.business_start = kwargs.get('business_start', 8)  # 8am
        self.business_end = kwargs.get('business_end', 18)    # 6pm
        
        # Emergency keywords for triage
        self.emergency_keywords = [
            'bleeding', 'unconscious', 'seizure', 'poisoned', 'hit by car',
            'cant breathe', 'choking', 'attacked', 'emergency', 'dying'
        ]
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours"""
        now = datetime.now()
        hour = now.hour
        # Monday-Friday = 0-4, Saturday = 5, Sunday = 6
        is_weekday = now.weekday() < 5
        
        return is_weekday and self.business_start <= hour < self.business_end
    
    def _detect_emergency(self, text: str) -> bool:
        """Detect emergency keywords in text"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.emergency_keywords)
    
    def _generate_twiml(self, message: str, gather: bool = False, 
                        action_url: str = None, menu_options: Dict = None) -> str:
        """Generate TwiML for voice response"""
        response = VoiceResponse()
        
        if gather:
            gather_obj = Gather(
                num_digits=1,
                action=action_url or '/twilio/handle-menu',
                timeout=5,
                method='POST'
            )
            gather_obj.say(message, voice='Polly.Joanna', language='en-US')
            
            if menu_options:
                options_text = ". ".join([f"Press {key} for {value}" for key, value in menu_options.items()])
                gather_obj.say(options_text, voice='Polly.Joanna', language='en-US')
            
            response.append(gather_obj)
            response.redirect('/twilio/handle-menu')  # Loop if no input
        else:
            response.say(message, voice='Polly.Joanna', language='en-US')
        
        return str(response)


def twilio_vet_answer_call(
    to: str,
    from_: str,
    greeting_text: str = None,
    practice_name: str = "Veterinary Practice",
    menu_enabled: bool = True,
    callback_url: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    AI-powered phone answering for veterinary practice
    
    Args:
        to: Calling phone number
        from_: Practice phone number (Twilio number)
        greeting_text: Custom greeting (optional)
        practice_name: Name of veterinary practice
        menu_enabled: Enable IVR menu (True/False)
        callback_url: URL for TwiML callbacks
        **kwargs: Additional Twilio options
    
    Returns:
        Dict with call_sid, twiml, status
    
    Raises:
        TwilioVeterinaryError: If call initiation fails
    """
    tools = TwilioVeterinaryTools(**kwargs)
    
    # Default greeting
    if not greeting_text:
        time_of_day = "morning" if datetime.now().hour < 12 else "afternoon" if datetime.now().hour < 18 else "evening"
        greeting_text = f"Thank you for calling {practice_name}. Good {time_of_day}."
    
    # Check business hours
    is_open = tools._is_business_hours()
    
    if not is_open:
        # After hours message
        after_hours_msg = (
            f"{greeting_text} Our office is currently closed. "
            "If this is an emergency, please press 1 to be connected to our emergency hotline. "
            "For all other inquiries, please press 2 to leave a message, "
            "or press 3 to receive information about our hours and location."
        )
        twiml = tools._generate_twiml(
            after_hours_msg,
            gather=True,
            action_url=callback_url or '/twilio/after-hours-menu',
            menu_options={'1': 'emergency', '2': 'voicemail', '3': 'information'}
        )
    else:
        # Business hours menu
        menu_msg = (
            f"{greeting_text} "
            "Press 1 to schedule an appointment. "
            "Press 2 to refill a prescription. "
            "Press 3 to speak with a veterinary technician. "
            "Press 4 for billing and insurance. "
            "Or stay on the line to speak with a receptionist."
        )
        twiml = tools._generate_twiml(
            menu_msg,
            gather=menu_enabled,
            action_url=callback_url or '/twilio/main-menu',
            menu_options={
                '1': 'appointments',
                '2': 'prescriptions',
                '3': 'vet tech',
                '4': 'billing'
            }
        )
    
    # Initiate call (for outbound) or return TwiML (for inbound webhook)
    try:
        result = {
            'success': True,
            'twiml': twiml,
            'is_business_hours': is_open,
            'greeting': greeting_text,
            'timestamp': datetime.now().isoformat()
        }
        
        # If initiating outbound call
        if kwargs.get('outbound'):
            call = tools.client.calls.create(
                to=to,
                from_=from_,
                twiml=twiml,
                status_callback=kwargs.get('status_callback'),
                timeout=kwargs.get('timeout', 60)
            )
            result['call_sid'] = call.sid
            result['status'] = call.status
        
        return result
        
    except Exception as e:
        raise TwilioVeterinaryError(f"Failed to answer call: {str(e)}")


def twilio_vet_route_call(
    call_sid: str,
    route_to: str,
    department: str = None,
    priority: str = "normal",
    **kwargs
) -> Dict[str, Any]:
    """
    Intelligent call routing to appropriate department/staff
    
    Args:
        call_sid: Twilio call SID
        route_to: Destination phone number or department
        department: Department name (appointments, emergency, billing)
        priority: Priority level (normal, high, emergency)
        **kwargs: Credential injection
    
    Returns:
        Dict with routing status and details
    
    Raises:
        TwilioVeterinaryError: If routing fails
    """
    tools = TwilioVeterinaryTools(**kwargs)
    
    try:
        # Department phone mapping (example)
        department_phones = {
            'appointments': kwargs.get('appointments_phone', '+15555550001'),
            'emergency': kwargs.get('emergency_phone', '+15555550002'),
            'billing': kwargs.get('billing_phone', '+15555550003'),
            'vet_tech': kwargs.get('vet_tech_phone', '+15555550004')
        }
        
        # Resolve route_to to phone number
        destination = department_phones.get(route_to, route_to)
        
        # Generate routing TwiML
        response = VoiceResponse()
        
        if priority == "emergency":
            response.say(
                "This is an emergency call. Connecting you immediately.",
                voice='Polly.Joanna',
                language='en-US'
            )
        else:
            response.say(
                f"Please hold while we connect you to {department or 'the appropriate department'}.",
                voice='Polly.Joanna',
                language='en-US'
            )
        
        # Dial with options
        dial = response.dial(
            timeout=30,
            action=kwargs.get('action_callback', '/twilio/call-complete'),
            method='POST'
        )
        dial.number(
            destination,
            status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
            status_callback=kwargs.get('status_callback')
        )
        
        # Update call with new TwiML
        call = tools.client.calls(call_sid).update(
            twiml=str(response)
        )
        
        return {
            'success': True,
            'call_sid': call_sid,
            'routed_to': destination,
            'department': department,
            'priority': priority,
            'status': call.status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise TwilioVeterinaryError(f"Failed to route call: {str(e)}")


def twilio_vet_handle_voicemail(
    call_sid: str,
    recording_url: str = None,
    transcription_text: str = None,
    caller_phone: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Process voicemail recording with transcription and AI analysis
    
    Args:
        call_sid: Twilio call SID
        recording_url: URL to voicemail recording (if available)
        transcription_text: Pre-transcribed text (optional)
        caller_phone: Caller's phone number
        **kwargs: Credential injection
    
    Returns:
        Dict with voicemail details, transcription, emergency flag
    
    Raises:
        TwilioVeterinaryError: If voicemail processing fails
    """
    tools = TwilioVeterinaryTools(**kwargs)
    
    try:
        # If no recording URL, fetch from call
        if not recording_url:
            recordings = tools.client.recordings.list(call_sid=call_sid, limit=1)
            if recordings:
                recording_url = f"https://api.twilio.com{recordings[0].uri.replace('.json', '.mp3')}"
        
        # Analyze voicemail content for emergencies
        is_emergency = False
        if transcription_text:
            is_emergency = tools._detect_emergency(transcription_text)
        
        result = {
            'success': True,
            'call_sid': call_sid,
            'recording_url': recording_url,
            'transcription': transcription_text or "[Transcription pending]",
            'caller_phone': caller_phone,
            'is_emergency': is_emergency,
            'timestamp': datetime.now().isoformat(),
            'requires_urgent_callback': is_emergency
        }
        
        # If emergency detected, send urgent notification
        if is_emergency:
            # Send SMS to practice owner/emergency contact
            emergency_contact = kwargs.get('emergency_contact_phone')
            if emergency_contact:
                tools.client.messages.create(
                    to=emergency_contact,
                    from_=tools.phone_number,
                    body=f"EMERGENCY VOICEMAIL from {caller_phone}:\n{transcription_text[:160]}\nListen: {recording_url}"
                )
                result['emergency_notification_sent'] = True
        
        return result
        
    except Exception as e:
        raise TwilioVeterinaryError(f"Failed to process voicemail: {str(e)}")


def twilio_vet_schedule_callback(
    phone: str,
    preferred_time: str,
    reason: str = None,
    patient_name: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Schedule callback request via SMS with confirmation
    
    Args:
        phone: Client phone number
        preferred_time: Preferred callback time (e.g., "2:00 PM today")
        reason: Reason for callback (optional)
        patient_name: Pet's name (optional)
        **kwargs: Credential injection
    
    Returns:
        Dict with scheduled callback details and SMS status
    
    Raises:
        TwilioVeterinaryError: If scheduling fails
    """
    tools = TwilioVeterinaryTools(**kwargs)
    
    try:
        # Format callback message
        patient_info = f" for {patient_name}" if patient_name else ""
        reason_info = f" regarding {reason}" if reason else ""
        
        message_body = (
            f"Thank you for your callback request{patient_info}{reason_info}. "
            f"We will call you back at {preferred_time}. "
            "Reply CONFIRM to confirm or RESCHEDULE to choose a different time."
        )
        
        # Send SMS
        message = tools.client.messages.create(
            to=phone,
            from_=tools.phone_number,
            body=message_body
        )
        
        return {
            'success': True,
            'message_sid': message.sid,
            'phone': phone,
            'preferred_time': preferred_time,
            'patient_name': patient_name,
            'reason': reason,
            'status': message.status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise TwilioVeterinaryError(f"Failed to schedule callback: {str(e)}")


def twilio_vet_send_appointment_reminder(
    phone: str,
    appointment_details: Dict[str, Any],
    hours_before: int = 24,
    **kwargs
) -> Dict[str, Any]:
    """
    Send automated appointment reminder via SMS
    
    Args:
        phone: Client phone number
        appointment_details: Dict with date, time, patient_name, vet_name
        hours_before: Hours before appointment to send (default: 24)
        **kwargs: Credential injection
    
    Returns:
        Dict with reminder status and message details
    
    Raises:
        TwilioVeterinaryError: If reminder fails
    """
    tools = TwilioVeterinaryTools(**kwargs)
    
    try:
        # Extract appointment info
        appt_date = appointment_details.get('date')
        appt_time = appointment_details.get('time')
        patient_name = appointment_details.get('patient_name', 'your pet')
        vet_name = appointment_details.get('vet_name', 'the veterinarian')
        practice_name = appointment_details.get('practice_name', 'our practice')
        
        # Format reminder message
        message_body = (
            f"Reminder: {patient_name} has an appointment with {vet_name} "
            f"at {practice_name} on {appt_date} at {appt_time}. "
            "Reply CONFIRM to confirm or CANCEL to cancel."
        )
        
        # Send SMS
        message = tools.client.messages.create(
            to=phone,
            from_=tools.phone_number,
            body=message_body,
            schedule_type='fixed' if hours_before > 0 else None,
            send_at=kwargs.get('send_at')  # ISO 8601 timestamp
        )
        
        return {
            'success': True,
            'message_sid': message.sid,
            'phone': phone,
            'appointment_date': appt_date,
            'appointment_time': appt_time,
            'patient_name': patient_name,
            'hours_before': hours_before,
            'status': message.status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise TwilioVeterinaryError(f"Failed to send reminder: {str(e)}")


def twilio_vet_emergency_triage(
    call_sid: str,
    symptoms: str,
    pet_species: str = None,
    pet_age: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    AI-powered emergency triage assessment
    
    Args:
        call_sid: Twilio call SID
        symptoms: Described symptoms from caller
        pet_species: Dog, cat, etc. (optional)
        pet_age: Pet's age (optional)
        **kwargs: Credential injection
    
    Returns:
        Dict with triage level, recommended actions, routing
    
    Raises:
        TwilioVeterinaryError: If triage fails
    """
    tools = TwilioVeterinaryTools(**kwargs)
    
    try:
        # Detect emergency keywords
        is_emergency = tools._detect_emergency(symptoms)
        
        # Emergency triage levels
        if is_emergency:
            triage_level = "CRITICAL"
            action = "Route to emergency hotline immediately"
            wait_time = "0 minutes - immediate"
        elif any(word in symptoms.lower() for word in ['vomiting', 'diarrhea', 'limping', 'coughing']):
            triage_level = "URGENT"
            action = "Schedule same-day appointment"
            wait_time = "2-4 hours"
        else:
            triage_level = "ROUTINE"
            action = "Schedule regular appointment within 2-3 days"
            wait_time = "24-48 hours"
        
        # Generate appropriate TwiML response
        response = VoiceResponse()
        
        if triage_level == "CRITICAL":
            response.say(
                "This sounds like an emergency. Connecting you to our emergency veterinarian now.",
                voice='Polly.Joanna',
                language='en-US'
            )
            # Dial emergency line
            response.dial(kwargs.get('emergency_phone', '+15555550911'))
        elif triage_level == "URGENT":
            response.say(
                "Based on the symptoms, we recommend a same-day appointment. "
                "Please hold while we check availability.",
                voice='Polly.Joanna',
                language='en-US'
            )
        else:
            response.say(
                "We can schedule an appointment for you within the next few days. "
                "Would you like to schedule now? Press 1 for yes, 2 to leave a message.",
                voice='Polly.Joanna',
                language='en-US'
            )
        
        # Update call if call_sid provided
        if call_sid:
            tools.client.calls(call_sid).update(twiml=str(response))
        
        return {
            'success': True,
            'call_sid': call_sid,
            'triage_level': triage_level,
            'symptoms': symptoms,
            'pet_species': pet_species,
            'pet_age': pet_age,
            'recommended_action': action,
            'estimated_wait': wait_time,
            'is_emergency': is_emergency,
            'twiml': str(response),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise TwilioVeterinaryError(f"Failed to triage emergency: {str(e)}")
