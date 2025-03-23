from django.shortcuts import render, redirect
from django.utils.timezone import now

from .models import Receipt



def upload_receipts(request):
    if request.method == 'POST':
        files = request.FILES.getlist('photos')
        for f in files:
            Receipt.objects.create(photo=f, owner=request.user, date=now())
        return redirect('admin')
    return render(request, 'receipt/upload.html')