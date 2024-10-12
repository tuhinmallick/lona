from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Teacher, Subject, Topic, LearningSession
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def is_teacher(user):
    return user.is_staff

@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

@login_required
def select_teacher(request):
    teachers = Teacher.objects.all()
    return render(request, 'select_teacher.html', {'teachers': teachers})

@login_required
def learning_session(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        subject_id = request.POST.get('subject_id')
        topic_id = request.POST.get('topic_id')

        teacher = Teacher.objects.get(id=teacher_id)
        topic = Topic.objects.get(id=topic_id)

        # Generate content using GPT-4
        gpt4_response = generate_gpt4_content(topic.content)

        # Convert text to speech using ElevenLabs API
        audio_url = text_to_speech(gpt4_response, teacher.voice_id)

        # Create learning session
        LearningSession.objects.create(student=request.user, teacher=teacher, topic=topic)

        return render(request, 'learning_session.html', {
            'content': gpt4_response,
            'audio_url': audio_url,
        })
    else:
        subjects = Subject.objects.all()
        return render(request, 'learning_session.html', {'subjects': subjects})

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    return render(request, 'teacher_dashboard.html')

@login_required
@user_passes_test(is_teacher)
def curriculum_upload(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        topic_name = request.POST.get('topic_name')
        content = request.POST.get('content')

        subject, _ = Subject.objects.get_or_create(name=subject_name)
        Topic.objects.create(subject=subject, name=topic_name, content=content)

        return redirect('teacher_dashboard')
    return render(request, 'curriculum_upload.html')

@login_required
@user_passes_test(is_teacher)
def voice_recording(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        # Upload audio file to ElevenLabs and get voice_id
        voice_id = upload_voice_to_elevenlabs(audio_file)
        
        teacher = Teacher.objects.get(user=request.user)
        teacher.voice_id = voice_id
        teacher.save()

        return redirect('teacher_dashboard')
    return render(request, 'voice_recording.html')

def generate_gpt4_content(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "system", "content": "You are a helpful teacher."}, {"role": "user", "content": prompt}],
        "max_tokens": 150
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()['choices'][0]['message']['content']

def text_to_speech(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    response = requests.post(url, json=data, headers=headers)
    # Save the audio file and return its URL
    # This is a simplified version, you'll need to implement file saving and URL generation
    return "path/to/audio/file.mp3"

def upload_voice_to_elevenlabs(audio_file):
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    files = {
        'files': audio_file,
        'name': 'Teacher Voice',
        'description': 'Custom teacher voice for AI Teacher app'
    }
    response = requests.post(url, headers=headers, files=files)
    return response.json()['voice_id']