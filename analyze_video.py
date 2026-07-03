import sys
from youtube_transcript_api import YouTubeTranscriptApi

def format_time(seconds):
    minutes = int(seconds) // 60
    sec = int(seconds) % 60
    return f"{minutes}:{sec:02d}"

def analyze_video(video_id):
    try:
        # Try fetching Indonesian transcript first, fallback to English or generated
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            transcript = transcript_list.find_transcript(['id', 'en']).fetch()
        except:
            # Fallback to whatever is available
            transcript = transcript_list.find_transcript(['id', 'en', 'en-US']).fetch()
            
        print(f"=== TRANSCRIPT ANALYSIS FOR {video_id} ===")
        
        # Group into 60-second chunks
        chunk_size = 60
        current_chunk_start = 0
        current_text = []
        
        for entry in transcript:
            start = entry['start']
            text = entry['text'].replace('\n', ' ')
            
            # If we've crossed into a new chunk
            if start >= current_chunk_start + chunk_size:
                # Print the previous chunk
                if current_text:
                    print(f"[{format_time(current_chunk_start)} - {format_time(current_chunk_start + chunk_size)}] {' '.join(current_text)}")
                current_chunk_start += chunk_size
                # Fast forward if there was a long gap
                while start >= current_chunk_start + chunk_size:
                    current_chunk_start += chunk_size
                current_text = [text]
            else:
                current_text.append(text)
                
        # Print the last chunk
        if current_text:
            print(f"[{format_time(current_chunk_start)} - {format_time(current_chunk_start + chunk_size)}] {' '.join(current_text)}")
            
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_video.py <video_id>")
    else:
        analyze_video(sys.argv[1])
