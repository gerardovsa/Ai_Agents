"""
FILE: tools/implementations/veterinary_soap_notes.py
PURPOSE: Voice-to-text SOAP note generation for veterinary practices

DEPENDENCIES:
- assemblyai ^1.0.0 (speech-to-text transcription)
- config (API key management for OpenAI/Claude)

EXPORTS:
- vet_soap_transcribe_recording(audio_file, **kwargs) - Transcribe voice recording
- vet_soap_generate_note(transcription, patient_name, **kwargs) - Format as SOAP note
- vet_soap_voice_to_note(audio_file, patient_name, **kwargs) - End-to-end conversion
- vet_soap_extract_vitals(transcription, **kwargs) - Extract vital signs from text
- vet_soap_identify_diagnoses(transcription, **kwargs) - Identify mentioned diagnoses
- vet_soap_generate_treatment_plan(assessment, **kwargs) - Generate treatment recommendations

USED BY:
- AI_infrastructure/routes/agent_routes.py (tool execution)
- veterinary mobile app (voice dictation workflow)
- exam room AI assistant (real-time note taking)

NOTES:
- Uses AssemblyAI for high-accuracy medical transcription
- GPT-4 formats transcription into SOAP structure (Subjective/Objective/Assessment/Plan)
- Extracts structured data: vitals, diagnoses, medications
- Cost: ~$0.05 per recording (300 seconds average)
- Integrates with PIMS for patient data enrichment

LAST MODIFIED: 2025-11-25 - Initial implementation for veterinary SOAP note automation
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# FIX (July 2026): Split the assemblyai/openai import from the
# `from config import get_api_key_enhanced` lookup. The two were bundled in
# a single try/except ImportError block, so when get_api_key_enhanced was
# missing from config.py, both libraries were wrongly reported as
# "not available — install with pip install …", even though they ARE
# installed in requirements.txt. Now: library imports stand on their own;
# the optional config-helper lookup falls back gracefully when absent.
try:
    import assemblyai as aai
except ImportError:
    aai = None
    print("AssemblyAI not available - install with: pip install assemblyai")

try:
    import openai
except ImportError:
    openai = None
    print("OpenAI not available - install with: pip install openai")

# Best-effort API-key resolution from config.py. Missing helper is non-fatal —
# callers can still pass keys explicitly via env or per-org vault.
try:
    from config import get_api_key_enhanced  # noqa: F401
    _has_get_api_key_enhanced = True
except ImportError:
    _has_get_api_key_enhanced = False

if _has_get_api_key_enhanced:
    if aai is not None:
        try:
            api_key = get_api_key_enhanced('ASSEMBLYAI_API_KEY')
            if api_key and hasattr(aai, 'settings'):
                aai.settings.api_key = api_key
        except Exception:  # noqa: BLE001
            pass
    if openai is not None:
        try:
            openai_key = get_api_key_enhanced('OPENAI_API_KEY')
            if openai_key:
                openai.api_key = openai_key
        except Exception:  # noqa: BLE001
            pass


class VeterinarySOAPError(Exception):
    """Custom exception for SOAP note operations"""
    pass


def vet_soap_transcribe_recording(
    audio_file: str,
    language: str = "en",
    speaker_labels: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Transcribe veterinary voice recording to text
    
    Args:
        audio_file: Path to audio file or URL
        language: Language code (default: "en")
        speaker_labels: Enable speaker diarization for vet/client
        **kwargs: Additional transcription options
    
    Returns:
        Dict with transcription text, speakers, confidence, duration
    
    Raises:
        VeterinarySOAPError: If transcription fails
    """
    if not aai:
        raise VeterinarySOAPError("AssemblyAI library not available")
    
    try:
        print(f"Transcribing veterinary recording: {audio_file}")
        
        # Configure transcription with medical vocabulary
        config = aai.TranscriptionConfig(
            language_code=language,
            speaker_labels=speaker_labels,
            punctuate=True,
            format_text=True,
            # Medical vocabulary boost (if supported by API)
            word_boost=kwargs.get('word_boost', [
                'parvo', 'heartworm', 'feline', 'canine', 'subcutaneous',
                'intramuscular', 'prednisone', 'cephalexin', 'meloxicam'
            ])
        )
        
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file, config=config)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise VeterinarySOAPError(f"Transcription failed: {transcript.error}")
        
        # Extract speaker segments if available
        speakers = []
        if speaker_labels and transcript.utterances:
            speakers = [
                {
                    'speaker': utt.speaker,
                    'text': utt.text,
                    'start': utt.start,
                    'end': utt.end,
                    'confidence': utt.confidence
                }
                for utt in transcript.utterances
            ]
        
        return {
            'success': True,
            'transcription': transcript.text,
            'speakers': speakers,
            'confidence': transcript.confidence,
            'audio_duration': transcript.audio_duration / 1000,  # Convert to seconds
            'words_count': len(transcript.words) if transcript.words else 0,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise VeterinarySOAPError(f"Failed to transcribe recording: {str(e)}")


def vet_soap_generate_note(
    transcription: str,
    patient_name: str,
    patient_species: str = None,
    patient_breed: str = None,
    patient_age: str = None,
    veterinarian_name: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate formatted SOAP note from transcription
    
    Args:
        transcription: Raw transcription text
        patient_name: Patient/pet name
        patient_species: Dog, cat, etc. (optional)
        patient_breed: Breed (optional)
        patient_age: Age (optional)
        veterinarian_name: Examining vet (optional)
        **kwargs: Additional formatting options
    
    Returns:
        Dict with formatted SOAP note sections
    
    Raises:
        VeterinarySOAPError: If note generation fails
    """
    if not openai:
        raise VeterinarySOAPError("OpenAI library not available")
    
    try:
        print(f"Generating SOAP note for patient: {patient_name}")
        
        # Build context for AI
        patient_info = f"Patient: {patient_name}"
        if patient_species:
            patient_info += f" ({patient_species}"
            if patient_breed:
                patient_info += f", {patient_breed}"
            if patient_age:
                patient_info += f", {patient_age}"
            patient_info += ")"
        
        vet_info = f"Veterinarian: {veterinarian_name}" if veterinarian_name else ""
        
        # Prompt for GPT-4 to format as SOAP
        prompt = f"""You are a veterinary medical assistant. Format the following veterinary examination transcription into a professional SOAP note.

{patient_info}
{vet_info}
Date: {datetime.now().strftime('%Y-%m-%d')}

TRANSCRIPTION:
{transcription}

FORMAT AS SOAP NOTE:
**S (Subjective):** Chief complaint, history from owner, symptoms observed at home
**O (Objective):** Physical exam findings, vital signs (TPR), diagnostic results
**A (Assessment):** Diagnosis or differential diagnoses
**P (Plan):** Treatment plan, medications prescribed, follow-up instructions

Extract and structure the information clearly. Include:
- Vital signs (Temperature, Pulse, Respiration) if mentioned
- Body weight if mentioned
- Specific medication names and dosages
- Follow-up timeline

Be concise and professional. Use veterinary medical terminology."""

        # Call GPT-4
        response = openai.ChatCompletion.create(
            model=kwargs.get('model', 'gpt-4'),
            messages=[
                {"role": "system", "content": "You are a veterinary medical assistant expert at formatting SOAP notes."},
                {"role": "user", "content": prompt}
            ],
            temperature=kwargs.get('temperature', 0.3),  # Lower temperature for consistency
            max_tokens=kwargs.get('max_tokens', 1500)
        )
        
        soap_note = response.choices[0].message.content
        
        # Parse SOAP sections using regex
        sections = {}
        section_pattern = r'\*\*([SOAP])\s*\(([^)]+)\):\*\*\s*([^*]+?)(?=\*\*[SOAP]|$)'
        matches = re.finditer(section_pattern, soap_note, re.DOTALL)
        
        for match in matches:
            section_letter = match.group(1)
            section_name = match.group(2)
            section_content = match.group(3).strip()
            
            section_key = {
                'S': 'subjective',
                'O': 'objective',
                'A': 'assessment',
                'P': 'plan'
            }.get(section_letter, section_name.lower())
            
            sections[section_key] = section_content
        
        return {
            'success': True,
            'patient_name': patient_name,
            'patient_species': patient_species,
            'soap_note_full': soap_note,
            'subjective': sections.get('subjective', ''),
            'objective': sections.get('objective', ''),
            'assessment': sections.get('assessment', ''),
            'plan': sections.get('plan', ''),
            'veterinarian': veterinarian_name,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'tokens_used': response.usage.total_tokens
        }
        
    except Exception as e:
        raise VeterinarySOAPError(f"Failed to generate SOAP note: {str(e)}")


def vet_soap_voice_to_note(
    audio_file: str,
    patient_name: str,
    patient_species: str = None,
    patient_breed: str = None,
    patient_age: str = None,
    veterinarian_name: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    End-to-end: Voice recording to formatted SOAP note
    
    Args:
        audio_file: Path to audio recording or URL
        patient_name: Patient/pet name
        patient_species: Dog, cat, etc. (optional)
        patient_breed: Breed (optional)
        patient_age: Age (optional)
        veterinarian_name: Examining vet (optional)
        **kwargs: Additional options
    
    Returns:
        Dict with transcription, SOAP note, extracted data
    
    Raises:
        VeterinarySOAPError: If conversion fails
    """
    try:
        print(f"Converting voice recording to SOAP note for {patient_name}")
        
        # Step 1: Transcribe audio
        transcription_result = vet_soap_transcribe_recording(
            audio_file,
            speaker_labels=kwargs.get('speaker_labels', True),
            **kwargs
        )
        
        if not transcription_result.get('success'):
            raise VeterinarySOAPError("Transcription failed")
        
        transcription = transcription_result['transcription']
        
        # Step 2: Generate SOAP note
        soap_result = vet_soap_generate_note(
            transcription,
            patient_name,
            patient_species,
            patient_breed,
            patient_age,
            veterinarian_name,
            **kwargs
        )
        
        if not soap_result.get('success'):
            raise VeterinarySOAPError("SOAP note generation failed")
        
        # Step 3: Extract vitals and diagnoses
        vitals = vet_soap_extract_vitals(transcription, **kwargs)
        diagnoses = vet_soap_identify_diagnoses(transcription, **kwargs)
        
        # Combine results
        return {
            'success': True,
            'patient_name': patient_name,
            'audio_file': audio_file,
            'audio_duration': transcription_result.get('audio_duration'),
            'transcription': transcription,
            'transcription_confidence': transcription_result.get('confidence'),
            'soap_note': soap_result.get('soap_note_full'),
            'subjective': soap_result.get('subjective'),
            'objective': soap_result.get('objective'),
            'assessment': soap_result.get('assessment'),
            'plan': soap_result.get('plan'),
            'vitals': vitals.get('vitals', {}),
            'diagnoses': diagnoses.get('diagnoses', []),
            'timestamp': datetime.now().isoformat(),
            'processing_time_seconds': transcription_result.get('audio_duration', 0) / 10  # Estimate
        }
        
    except Exception as e:
        raise VeterinarySOAPError(f"Failed to convert voice to SOAP note: {str(e)}")


def vet_soap_extract_vitals(
    transcription: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Extract vital signs from transcription text
    
    Args:
        transcription: Transcription text
        **kwargs: Additional options
    
    Returns:
        Dict with extracted vitals (temperature, pulse, respiration, weight)
    
    Raises:
        VeterinarySOAPError: If extraction fails
    """
    try:
        vitals = {}
        
        # Temperature (Fahrenheit)
        temp_match = re.search(r'temperature[:\s]+(\d+\.?\d*)\s*(?:degrees?|°|F)', transcription, re.IGNORECASE)
        if temp_match:
            vitals['temperature'] = float(temp_match.group(1))
            vitals['temperature_unit'] = 'F'
        
        # Pulse/Heart Rate (BPM)
        pulse_match = re.search(r'(?:pulse|heart\s*rate)[:\s]+(\d+)\s*(?:bpm|beats)', transcription, re.IGNORECASE)
        if pulse_match:
            vitals['pulse'] = int(pulse_match.group(1))
            vitals['pulse_unit'] = 'bpm'
        
        # Respiration Rate (breaths per minute)
        resp_match = re.search(r'respiration[:\s]+(\d+)\s*(?:breaths|bpm)', transcription, re.IGNORECASE)
        if resp_match:
            vitals['respiration'] = int(resp_match.group(1))
            vitals['respiration_unit'] = 'breaths/min'
        
        # Weight (pounds or kg)
        weight_match = re.search(r'weight[:\s]+(\d+\.?\d*)\s*(lbs?|pounds?|kg|kilograms?)', transcription, re.IGNORECASE)
        if weight_match:
            vitals['weight'] = float(weight_match.group(1))
            vitals['weight_unit'] = 'lbs' if 'lb' in weight_match.group(2).lower() else 'kg'
        
        return {
            'success': True,
            'vitals': vitals,
            'vitals_count': len(vitals)
        }
        
    except Exception as e:
        raise VeterinarySOAPError(f"Failed to extract vitals: {str(e)}")


def vet_soap_identify_diagnoses(
    transcription: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Identify mentioned diagnoses/conditions from transcription
    
    Args:
        transcription: Transcription text
        **kwargs: Additional options
    
    Returns:
        Dict with identified diagnoses
    
    Raises:
        VeterinarySOAPError: If identification fails
    """
    try:
        # Common veterinary diagnoses to detect
        common_diagnoses = [
            'parvovirus', 'distemper', 'kennel cough', 'heartworm',
            'flea allergy', 'ear infection', 'urinary tract infection',
            'diabetes', 'arthritis', 'hip dysplasia', 'pancreatitis',
            'gastroenteritis', 'foreign body', 'skin infection',
            'upper respiratory infection', 'pneumonia', 'conjunctivitis'
        ]
        
        found_diagnoses = []
        transcription_lower = transcription.lower()
        
        for diagnosis in common_diagnoses:
            if diagnosis in transcription_lower:
                found_diagnoses.append({
                    'diagnosis': diagnosis.title(),
                    'confidence': 'mentioned'
                })
        
        return {
            'success': True,
            'diagnoses': found_diagnoses,
            'diagnoses_count': len(found_diagnoses)
        }
        
    except Exception as e:
        raise VeterinarySOAPError(f"Failed to identify diagnoses: {str(e)}")


def vet_soap_generate_treatment_plan(
    assessment: str,
    diagnoses: List[str] = None,
    patient_species: str = None,
    patient_weight: float = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate treatment plan recommendations based on assessment
    
    Args:
        assessment: Assessment section from SOAP note
        diagnoses: List of identified diagnoses (optional)
        patient_species: Dog, cat, etc. (optional)
        patient_weight: Patient weight for dosage calculations (optional)
        **kwargs: Additional options
    
    Returns:
        Dict with treatment recommendations, medications, follow-up
    
    Raises:
        VeterinarySOAPError: If generation fails
    """
    if not openai:
        raise VeterinarySOAPError("OpenAI library not available")
    
    try:
        print("Generating treatment plan recommendations")
        
        # Build context
        context = f"Assessment: {assessment}"
        if diagnoses:
            context += f"\nDiagnoses: {', '.join(diagnoses)}"
        if patient_species:
            context += f"\nSpecies: {patient_species}"
        if patient_weight:
            context += f"\nWeight: {patient_weight} lbs"
        
        prompt = f"""You are a veterinary medical expert. Based on the following assessment, provide treatment recommendations.

{context}

Provide:
1. Medications (generic names, dosages, frequency)
2. Supportive care instructions
3. Dietary recommendations if applicable
4. Follow-up timeline
5. Warning signs to watch for

Format as clear bullet points."""

        response = openai.ChatCompletion.create(
            model=kwargs.get('model', 'gpt-4'),
            messages=[
                {"role": "system", "content": "You are a veterinary medical expert providing treatment recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=800
        )
        
        treatment_plan = response.choices[0].message.content
        
        return {
            'success': True,
            'treatment_plan': treatment_plan,
            'assessment': assessment,
            'diagnoses': diagnoses or [],
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise VeterinarySOAPError(f"Failed to generate treatment plan: {str(e)}")
