from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import Teacher, Subject, Topic, LearningSession, TeacherVoice
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

def get_topics(request):
    subject_id = request.GET.get('subject_id')
    topics = Topic.objects.filter(subject_id=subject_id).values('id', 'name')
    return JsonResponse(list(topics), safe=False)

@login_required
def learning_session(request):
    teacher, created = Teacher.objects.get_or_create(user=request.user)
    # topic, created = Topic.objects.get_or_create(name='Introduction to Python', content='Python is a high-level programming language that is widely used for web development, data analysis, artificial intelligence, and scientific computing.')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        subject_id = request.POST.get('subject_id')
        topic_id = request.POST.get('topic_id')

        teacher = Teacher.objects.get(id=teacher_id)
        topic = Topic.objects.get(id=topic_id)
        subject = Subject.objects.get(id=subject_id)

        # Get the appropriate voice
        teacher_voice = TeacherVoice.objects.filter(teacher=teacher, subject=subject).first()
        if not teacher_voice:
            teacher_voice = TeacherVoice.objects.filter(teacher=teacher, subject=None).first()

        if not teacher_voice:
            return render(request, 'error.html', {'message': 'No voice recording available for this teacher and subject.'})

        # Generate content using GPT-4
        gpt4_response = generate_gpt4_content(topic.content)

        # Convert text to speech using ElevenLabs API
        audio_url = text_to_speech(gpt4_response, teacher_voice.voice_id)

        # Create learning session
        LearningSession.objects.create(student=request.user, teacher=teacher, topic=topic)

        return render(request, 'learning_session.html', {
            'content': gpt4_response,
            'audio_url': audio_url,
        })
    else:
        subjects = Subject.objects.all()
        initial_subject = subjects.first()
        topics = Topic.objects.filter(subject=initial_subject) if initial_subject else []
        return render(request, 'learning_session.html', {'subjects': subjects, 'topics': topics})

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
    # Get or create the Teacher object for the current user
    teacher, created = Teacher.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        subject_id = request.POST.get('subject_id')
        description = request.POST.get('description')

        if not audio_file:
            return render(request, 'voice_recording.html', {'error': 'No audio file provided.'})

        subject = Subject.objects.get(id=subject_id) if subject_id else None

        # Upload voice to ElevenLabs and get voice_id
        voice_id = upload_voice_to_elevenlabs(audio_file, description)

        if voice_id:
            TeacherVoice.objects.create(
                teacher=teacher,
                subject=subject,
                voice_id=voice_id,
                description=description
            )
            return redirect('teacher_dashboard')
        else:
            return render(request, 'voice_recording.html', {'error': 'Failed to upload voice to ElevenLabs.'})

    subjects = Subject.objects.all()
    return render(request, 'voice_recording.html', {'subjects': subjects})

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

def upload_voice_to_elevenlabs(audio_file, description):
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    files = {
        'files': (audio_file.name, audio_file, audio_file.content_type),
        'name': (None, f"{description[:20]}"),  # Use the first 20 characters of the description as the name
        'description': (None, description)
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        return response.json().get('voice_id')
    except requests.exceptions.RequestException as e:
        print(f"Error uploading voice to ElevenLabs: {e}")
        return None


