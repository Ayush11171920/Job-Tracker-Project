from django.shortcuts import render,redirect,get_object_or_404
from .models import JobApplication
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

@login_required(login_url='login')
def dashboard(request):
    jobs = JobApplication.objects.filter(user=request.user)

    status_filter = request.GET.get("status")

    if status_filter:
        jobs = jobs.filter(status=status_filter)

    total = JobApplication.objects.filter(user=request.user).count()
    applied = JobApplication.objects.filter(user=request.user, status="Applied").count()
    interview = JobApplication.objects.filter(user=request.user, status="Interview").count()
    offer = JobApplication.objects.filter(user=request.user, status="Offer").count()
    rejected = JobApplication.objects.filter(user=request.user, status="Rejected").count()

    context = {
        "jobs": jobs,
        "total": total,
        "applied": applied,
        "interview": interview,
        "offer": offer,
        "rejected": rejected,
        "current_status": status_filter
    }

    return render(request, "dashboard.html", context)



def add_job(request):
    return render(request, 'add_job.html')

@login_required
def add_job(request):
    if request.method == 'POST':
        company = request.POST.get('company')
        position = request.POST.get('position')
        status = request.POST.get('status')

        JobApplication.objects.create(
            user=request.user,
            company=company,
            position=position,
            status=status
        )

        return redirect('dashboard')

    return render(request, 'add_job.html')

@login_required(login_url='login')
def edit_job(request, id):
    job = get_object_or_404(JobApplication, id=id, user=request.user)

    if request.method == 'POST':
        job.company = request.POST.get('company')
        job.position = request.POST.get('position')
        job.status = request.POST.get('status')
        job.save()
        return redirect('dashboard')

    return render(request, 'edit_job.html', {'job': job})

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

