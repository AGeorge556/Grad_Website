import requests
import json
import time

def test_talking_head_api():
    print("Testing talking head generation...")
    
    # Test the talking head generation API
    url = "http://localhost:8000/videos/104/talking-head"
    
    try:
        # Make the API call
        response = requests.get(url)
        
        # Print the response status and content
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # If successful, try to access the video URL
        if response.status_code == 200:
            video_url = response.json().get("talking_head_url")
            if video_url:
                print(f"Video URL: {video_url}")
                # Try to access the video URL
                video_response = requests.get(f"http://localhost:8000{video_url}")
                print(f"Video response status: {video_response.status_code}")
                if video_response.status_code == 200:
                    print("Successfully accessed the video!")
                    # Check content type to verify it's a video
                    content_type = video_response.headers.get("Content-Type")
                    print(f"Content-Type: {content_type}")
                    if "video" in content_type:
                        print("Confirmed that the response is a video file.")
                    else:
                        print("Warning: Response doesn't appear to be a video file.")
            else:
                print("No video URL in the response.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_talking_head_api() 