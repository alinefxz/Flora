from django.shortcuts import render
from django.views import View

class DashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'saude/dashboard.html')

    def post(self, request):
        pass