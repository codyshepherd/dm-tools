from django.http import HttpResponse
from django.shortcuts import render
from plebs import plebs


def index(request):
    return HttpResponse(plebs.web_make(1))


