from django.shortcuts import render,redirect,get_object_or_404
from .models import JobApplication
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import JobApplication
from rest_framework.viewsets import ModelViewSet
from .serializers import JobApplicationSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.models import User



@login_required(login_url='login')
def dashboard(request):
    # 👇 Get user jobs
    jobs = JobApplication.objects.filter(user=request.user)

    # 👇 Filter by status
    status_filter = request.GET.get("status")
    if status_filter:
        jobs = jobs.filter(status=status_filter)

    # 👇 Dashboard stats
    total = JobApplication.objects.filter(user=request.user).count()
    applied = JobApplication.objects.filter(user=request.user, status="Applied").count()
    interview = JobApplication.objects.filter(user=request.user, status="Interview").count()
    offer = JobApplication.objects.filter(user=request.user, status="Offer").count()
    rejected = JobApplication.objects.filter(user=request.user, status="Rejected").count()

    # =========================
    # 🤖 AI PART (CLEAN)
    # =========================
    questions = None
    selected_job_id = None

    if request.method == "POST":
        job_id = request.POST.get("job_id")

        if job_id:
            selected_job_id = job_id

            job = JobApplication.objects.get(id=job_id, user=request.user)
            role = job.position

            url = "https://openrouter.ai/api/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Generate 5 interview questions for a {role} role."
                    }
                ]
            }

            try:
                response = requests.post(url, headers=headers, json=data)
                result = response.json()

                questions = result['choices'][0]['message']['content']

            except Exception as e:
                questions = f"Error: {str(e)}"

    # =========================
    # 📦 Context
    # =========================
    context = {
        "jobs": jobs,
        "total": total,
        "applied": applied,
        "interview": interview,
        "offer": offer,
        "rejected": rejected,
        "current_status": status_filter,
        "questions": questions,
        "selected_job_id": selected_job_id,
    }

    return render(request, "dashboard.html", context)

# @login_required(login_url='login')
# def dashboard(request):
#     jobs = JobApplication.objects.filter(user=request.user)

#     status_filter = request.GET.get("status")

#     if status_filter:
#         jobs = jobs.filter(status=status_filter)

#     total = JobApplication.objects.filter(user=request.user).count()
#     applied = JobApplication.objects.filter(user=request.user, status="Applied").count()
#     interview = JobApplication.objects.filter(user=request.user, status="Interview").count()
#     offer = JobApplication.objects.filter(user=request.user, status="Offer").count()
#     rejected = JobApplication.objects.filter(user=request.user, status="Rejected").count()

#     context = {
#         "jobs": jobs,
#         "total": total,
#         "applied": applied,
#         "interview": interview,
#         "offer": offer,
#         "rejected": rejected,
#         "current_status": status_filter
#     }

#     return render(request, "dashboard.html", context)



def add_job(request):
    return render(request, 'add_job.html')

@login_required
def add_job(request):
    if request.method == 'POST':
        company = request.POST.get('company')
        position = request.POST.get('position')
        status = request.POST.get('status')
        
        try:
          JobApplication.objects.create(
            user=request.user,
            company=company,
            position=position,
            status=status
          )
          messages.success(request,"Job added successfully")
        
        except IntegrityError:
           messages.error(request,"This job already exists")
        
        return redirect("dashboard")
    
         

    return render(request, 'add_job.html')

@login_required(login_url='login')

def edit_job(request, job_id):
    job = get_object_or_404(JobApplication, id=job_id, user=request.user)

    if request.method == "POST":
        company = request.POST.get("company")
        position = request.POST.get("position")
        status = request.POST.get("status")

        # 🔍 Check duplicate EXCLUDING current job
        exists = JobApplication.objects.filter(
            user=request.user,
            company=company,
            position=position
        ).exclude(id=job.id).exists()

        if exists:
            messages.error(request, "This job already exists!")
            return redirect("dashboard")

        # ✅ Safe to update
        job.company = company
        job.position = position
        job.status = status
        job.save()

        messages.success(request, "Job updated successfully!")
        return redirect("dashboard")

    return render(request, "edit_job.html", {"job": job})

@login_required(login_url='login')
def delete_job(request, id):
    job = get_object_or_404(JobApplication, id=id, user=request.user)

    if request.method == "POST":
        job.delete()
        return redirect('dashboard')

    return render(request, 'delete_job.html', {'job': job})



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "signup.html")


class JobApplicationViewSet(ModelViewSet):
    queryset = JobApplication.objects.all()   
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=1)


@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    
    return Response({'error': 'Invalid credentials'})




@api_view(['POST'])
def generate_questions(request):
    role = request.data.get('role')

    if not role:
        return Response({"error": "Role is required"})

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": f"Generate 5 interview questions for a {role} role. Keep them short and practical."
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        questions = result['choices'][0]['message']['content']

        return Response({"questions": questions})

    except Exception as e:
        return Response({"error": str(e)})
    

def ai_questions_page(request):
    questions = None

    if request.method == "POST":
        role = request.POST.get("role")

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": f"Generate 5 interview questions for a {role} role."
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        questions = result['choices'][0]['message']['content']

    return render(request, 'ai_questions.html', {'questions': questions})   