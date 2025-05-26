from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Receipt
from .forms import ReceiptForm, ReceiptItemFormSet

def receipt_edit(request: WSGIRequest, pk: int) -> HttpResponse:
    receipt = get_object_or_404(Receipt, pk=pk)

    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt, user=request.user)
        formset = ReceiptItemFormSet(request.POST, instance=receipt)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('index')
    else:
        form = ReceiptForm(instance=receipt, user=request.user)
        formset = ReceiptItemFormSet(instance=receipt)

    return render(request, 'receipt/receipt_form.html', {
        'form': form,
        'formset': formset,
        'receipt': receipt,
    })


def receipt_delete(request: WSGIRequest, pk: int) -> HttpResponse:
    if request.method == 'POST':
        receipt = get_object_or_404(Receipt, pk=pk)
        receipt.delete()
    return redirect('index')
