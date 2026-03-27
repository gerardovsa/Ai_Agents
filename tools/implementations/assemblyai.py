"""
AssemblyAI Tool Implementations
================================

This module provides tool implementations for AssemblyAI transcription and analysis.

CREDENTIALS: Uses user_platform_credentials table (Dec 5, 2025)
- Platform: 'assemblyai'
- Falls back to environment variable if no user credentials
"""

import os

try:
    import assemblyai as aai
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    print("⚠️ AssemblyAI not available - install with: pip install assemblyai")
    aai = None
    ASSEMBLYAI_AVAILABLE = False


def _get_assemblyai_client(user_id: int = None):
    """
    Get AssemblyAI client with user-specific credentials
    
    Args:
        user_id: User ID from authentication (optional)
    
    Returns:
        Configured AssemblyAI client or None
    """
    if not ASSEMBLYAI_AVAILABLE:
        return None
    
    # Try user-specific credentials first — uses full 3-tier resolver (user → org → env)
    if user_id:
        try:
            from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
            api_key = resolve_api_key(user_id, 'assemblyai')
            if api_key:
                print(f"[AssemblyAI] ✅ Using resolved credentials (user_id={user_id})")
                aai.settings.api_key = api_key
                return aai
        except Exception as e:
            print(f"[AssemblyAI] ⚠️ Could not load user credentials: {e}")
    
    # Fallback to environment variable
    try:
        from config import get_api_key_enhanced
        api_key = get_api_key_enhanced('ASSEMBLYAI_API_KEY')
    except:
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
    
    if api_key and hasattr(aai, 'settings'):
        print("[AssemblyAI] ✅ Using environment variable credentials")
        aai.settings.api_key = api_key
        return aai
    
    print("[AssemblyAI] ❌ No API key found")
    return None


def assemblyai_transcribe(audio_file: str, language: str = "en", speaker_labels: bool = False, punctuate: bool = True, user_id: int = None):
    """
    Transcribe audio or video file to text.
    
    Args:
        audio_file: Path to audio/video file or URL
        language: Language code (e.g., 'en', 'es')
        speaker_labels: Enable speaker diarization
        punctuate: Add punctuation
        user_id: User ID from authentication (for user-specific API key)
    
    Returns:
        Transcription result with text
    """
    client = _get_assemblyai_client(user_id)
    if not client:
        return {
            'success': False,
            'error': 'AssemblyAI not available or no API key configured'
        }
    
    print(f"🔧 Transcribing audio: {audio_file}")
    
    try:
        config = client.TranscriptionConfig(
            language_code=language,
            speaker_labels=speaker_labels,
            punctuate=punctuate
        )
        
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file, config=config)
        
        result = {
            'id': transcript.id,
            'text': transcript.text,
            'status': transcript.status,
            'language': language
        }
        
        if speaker_labels and transcript.utterances:
            result['utterances'] = [
                {
                    'speaker': u.speaker,
                    'text': u.text,
                    'start': u.start,
                    'end': u.end
                }
                for u in transcript.utterances
            ]
        
        return result
        
    except Exception as e:
        print(f" Transcription failed: {e}")
        raise


def assemblyai_analyze(audio_file: str, sentiment_analysis: bool = True, 
                       auto_chapters: bool = False, entity_detection: bool = False, user_id: int = None):
    """
    Analyze audio for sentiment, topics, and entities.
    
    Args:
        audio_file: Path to audio file or URL
        sentiment_analysis: Enable sentiment analysis
        auto_chapters: Generate chapter markers
        entity_detection: Detect named entities
        user_id: User ID from authentication (for user-specific API key)
    
    Returns:
        Analysis results
    """
    client = _get_assemblyai_client(user_id)
    if not client:
        return {
            'success': False,
            'error': 'AssemblyAI not available or no API key configured'
        }
    
    print(f"🔧 Analyzing audio: {audio_file}")
    
    try:
        config = client.TranscriptionConfig(
            sentiment_analysis=sentiment_analysis,
            auto_chapters=auto_chapters,
            entity_detection=entity_detection
        )
        
        transcriber = client.Transcriber()
        transcript = transcriber.transcribe(audio_file, config=config)
        
        result = {
            'id': transcript.id,
            'text': transcript.text,
            'status': transcript.status
        }
        
        if sentiment_analysis and transcript.sentiment_analysis_results:
            result['sentiment'] = [
                {
                    'text': s.text,
                    'sentiment': s.sentiment,
                    'confidence': s.confidence
                }
                for s in transcript.sentiment_analysis_results
            ]
        
        if auto_chapters and transcript.chapters:
            result['chapters'] = [
                {
                    'summary': c.summary,
                    'headline': c.headline,
                    'start': c.start,
                    'end': c.end
                }
                for c in transcript.chapters
            ]
        
        if entity_detection and transcript.entities:
            result['entities'] = [
                {
                    'text': e.text,
                    'entity_type': e.entity_type,
                    'start': e.start,
                    'end': e.end
                }
                for e in transcript.entities
            ]
        
        return result
        
    except Exception as e:
        print(f" Analysis failed: {e}")
        raise


def assemblyai_speakers(audio_file: str, speakers_expected: int = None, user_id: int = None):
    """
    Identify and label different speakers in audio.
    
    Args:
        audio_file: Path to audio file or URL
        speakers_expected: Expected number of speakers (optional)
        user_id: User ID from authentication (for user-specific API key)
    
    Returns:
        Speaker diarization results
    """
    client = _get_assemblyai_client(user_id)
    if not client:
        return {
            'success': False,
            'error': 'AssemblyAI not available or no API key configured'
        }
    
    print(f"🔧 Identifying speakers in: {audio_file}")
    
    try:
        config = client.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=speakers_expected
        )
        
        transcriber = client.Transcriber()
        transcript = transcriber.transcribe(audio_file, config=config)
        
        speakers = {}
        for utterance in transcript.utterances:
            speaker = utterance.speaker
            if speaker not in speakers:
                speakers[speaker] = {
                    'utterances': [],
                    'total_time': 0
                }
            
            speakers[speaker]['utterances'].append({
                'text': utterance.text,
                'start': utterance.start,
                'end': utterance.end
            })
            speakers[speaker]['total_time'] += (utterance.end - utterance.start)
        
        return {
            'id': transcript.id,
            'speakers': speakers,
            'speaker_count': len(speakers)
        }
        
    except Exception as e:
        print(f" Speaker identification failed: {e}")
        raise


def assemblyai_status(transcript_id: str, user_id: int = None):
    """
    Check status of a transcription job.
    
    Args:
        transcript_id: AssemblyAI transcript ID
        user_id: User ID from authentication (for user-specific API key)
    
    Returns:
        Transcription status
    """
    client = _get_assemblyai_client(user_id)
    if not client:
        return {
            'success': False,
            'error': 'AssemblyAI not available or no API key configured'
        }
    
    print(f"🔧 Checking transcript status: {transcript_id}")
    
    try:
        transcript = client.Transcript.get_by_id(transcript_id)
        
        return {
            'id': transcript.id,
            'status': transcript.status,
            'text': transcript.text if transcript.status == 'completed' else None,
            'error': transcript.error if transcript.status == 'error' else None
        }
        
    except Exception as e:
        print(f" Status check failed: {e}")
        raise


if __name__ == "__main__":
    print("AssemblyAI tools loaded")
