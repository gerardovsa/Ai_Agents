"""
AssemblyAI Tool Implementations
================================

This module provides tool implementations for AssemblyAI transcription and analysis.
"""

import os
import assemblyai as aai

try:
    from config import get_api_key_enhanced
    aai.settings.api_key = get_api_key_enhanced('ASSEMBLYAI_API_KEY')
except ImportError:
    aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')


def assemblyai_transcribe(audio_file: str, language: str = "en", speaker_labels: bool = False, punctuate: bool = True):
    """
    Transcribe audio or video file to text.
    
    Args:
        audio_file: Path to audio/video file or URL
        language: Language code (e.g., 'en', 'es')
        speaker_labels: Enable speaker diarization
        punctuate: Add punctuation
    
    Returns:
        Transcription result with text
    """
    print(f"🔧 Transcribing audio: {audio_file}")
    
    try:
        config = aai.TranscriptionConfig(
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
        print(f"❌ Transcription failed: {e}")
        raise


def assemblyai_analyze(audio_file: str, sentiment_analysis: bool = True, 
                       auto_chapters: bool = False, entity_detection: bool = False):
    """
    Analyze audio for sentiment, topics, and entities.
    
    Args:
        audio_file: Path to audio file or URL
        sentiment_analysis: Enable sentiment analysis
        auto_chapters: Generate chapter markers
        entity_detection: Detect named entities
    
    Returns:
        Analysis results
    """
    print(f"🔧 Analyzing audio: {audio_file}")
    
    try:
        config = aai.TranscriptionConfig(
            sentiment_analysis=sentiment_analysis,
            auto_chapters=auto_chapters,
            entity_detection=entity_detection
        )
        
        transcriber = aai.Transcriber()
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
        print(f"❌ Analysis failed: {e}")
        raise


def assemblyai_speakers(audio_file: str, speakers_expected: int = None):
    """
    Identify and label different speakers in audio.
    
    Args:
        audio_file: Path to audio file or URL
        speakers_expected: Expected number of speakers (optional)
    
    Returns:
        Speaker diarization results
    """
    print(f"🔧 Identifying speakers in: {audio_file}")
    
    try:
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=speakers_expected
        )
        
        transcriber = aai.Transcriber()
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
        print(f"❌ Speaker identification failed: {e}")
        raise


def assemblyai_status(transcript_id: str):
    """
    Check status of a transcription job.
    
    Args:
        transcript_id: AssemblyAI transcript ID
    
    Returns:
        Transcription status
    """
    print(f"🔧 Checking transcript status: {transcript_id}")
    
    try:
        transcript = aai.Transcript.get_by_id(transcript_id)
        
        return {
            'id': transcript.id,
            'status': transcript.status,
            'text': transcript.text if transcript.status == 'completed' else None,
            'error': transcript.error if transcript.status == 'error' else None
        }
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        raise


if __name__ == "__main__":
    print("AssemblyAI tools loaded")
