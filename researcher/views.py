from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .tasks import process_research, compare_profiles, process_document
from .models import CompanyProfile, Workspace, CompanyDocument, ChatMessage, MarketTrend
from .chatbot import ChatbotRAG
from .utils import markdown_to_html
import json

class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            workspaces = Workspace.objects.filter(user=request.user).order_by('-created_at')
            if workspaces.exists():
                return redirect('workspace_detail', workspace_id=workspaces.first().id)
            return render(request, "index.html", {"workspaces": workspaces})
        return render(request, "index.html")

class WorkspaceListView(LoginRequiredMixin, ListView):
    model = Workspace
    template_name = 'workspaces.html'
    context_object_name = 'workspaces'
    
    def get_queryset(self):
        return Workspace.objects.filter(user=self.request.user).order_by('-created_at')

class WorkspaceCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "workspace_create.html")
    
    def post(self, request):
        workspace_name = request.POST.get("workspace_name")
        if workspace_name:
            workspace = Workspace.objects.create(
                user=request.user,
                name=workspace_name
            )
            return redirect('workspace_detail', workspace_id=workspace.id)
        messages.error(request, "Workspace name is required")
        return redirect('workspace_create')

class WorkspaceDetailView(LoginRequiredMixin, View):
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        companies = CompanyProfile.objects.filter(workspace=workspace).order_by('-created_at')
        return render(request, "workspace_detail.html", {
            "workspace": workspace,
            "companies": companies
        })

class ResearchCompanyView(LoginRequiredMixin, View):
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        return render(request, "research_company.html", {"workspace": workspace})
    
    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        company_name = request.POST.get("company_name")

        if company_name:
            # Check if workspace has reached the limit of 3 companies
            if workspace.get_companies_count() >= 3:
                messages.error(request, "Workspace already has 3 companies. Please remove a company or create a new workspace.")
                return redirect('workspace_detail', workspace_id=workspace.id)
                
            process_research(workspace.id, company_name)
            messages.success(request, f"Research process started for {company_name}")
            return redirect('workspace_detail', workspace_id=workspace.id)
        
        messages.error(request, "Company name is required")
        return redirect('research_company', workspace_id=workspace.id)

class CompanyDetailView(LoginRequiredMixin, View):
    def get(self, request, workspace_id, profile_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        try:
            profile = get_object_or_404(CompanyProfile, id=profile_id, workspace=workspace)
            documents = CompanyDocument.objects.filter(company=profile).order_by('-uploaded_at')
            
            # Convert markdown to HTML
            profile.profile_content = markdown_to_html(profile.profile_content)
            
            return render(request, "company_detail.html", {
                "workspace": workspace,
                "profile": profile,
                "documents": documents
            })
        except CompanyProfile.DoesNotExist:
            messages.error(request, "Company profile not found")
            return redirect('workspace_detail', workspace_id=workspace.id)

class CompareCompaniesView(LoginRequiredMixin, View):
    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        companies = CompanyProfile.objects.filter(workspace=workspace).order_by('-created_at')
        return render(request, "compare.html", {
            "workspace": workspace,
            "companies": companies
        })
    
    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        profile_id1 = request.POST.get("profile_id1")
        profile_id2 = request.POST.get("profile_id2")
        profile_id3 = request.POST.get("profile_id3")
        
        profile_ids = [pid for pid in [profile_id1, profile_id2, profile_id3] if pid]
        
        if len(profile_ids) >= 2:
            compare_profiles(profile_ids)
            messages.success(request, "Comparison process started")
        else:
            messages.error(request, "Please select at least two companies to compare")
            
        return render(request, "compare.html", {
            "workspace": workspace,
            "companies": CompanyProfile.objects.filter(workspace=workspace).order_by('-created_at'),
            "comparison_requested": True,
            "selected_profiles": profile_ids
        })

class UploadDocumentView(LoginRequiredMixin, View):
    def post(self, request, workspace_id, profile_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        profile = get_object_or_404(CompanyProfile, id=profile_id, workspace=workspace)
        
        document = request.FILES.get('document')
        document_title = request.POST.get('document_title')
        document_type = request.POST.get('document_type')
        
        if document and document_title and document_type:
            # Save the document
            path = default_storage.save(f'company_documents/{document.name}', ContentFile(document.read()))
            
            # Create document record
            company_document = CompanyDocument.objects.create(
                company=profile,
                title=document_title,
                document_type=document_type,
                file=path
            )
            
            # Process the document in background
            process_document(company_document.id)
            
            messages.success(request, f"Document '{document_title}' uploaded and is being processed")
        else:
            messages.error(request, "Please provide all required document information")
            
        return redirect('company_detail', workspace_id=workspace_id, profile_id=profile_id)

class DeleteCompanyView(LoginRequiredMixin, View):
    def post(self, request, workspace_id, profile_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        profile = get_object_or_404(CompanyProfile, id=profile_id, workspace=workspace)
        
        company_name = profile.company_name
        profile.delete()
        
        messages.success(request, f"Company '{company_name}' has been removed from workspace")
        return redirect('workspace_detail', workspace_id=workspace_id)

class DeleteWorkspaceView(LoginRequiredMixin, View):
    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
        
        workspace_name = workspace.name
        workspace.delete()
        
        messages.success(request, f"Workspace '{workspace_name}' has been deleted")
        return redirect('workspace_list')

@login_required
def chat_view(request, workspace_id):
    """View for the chatbot interface"""
    workspace = get_object_or_404(Workspace, id=workspace_id, user=request.user)
    chat_history = ChatMessage.objects.filter(workspace=workspace).order_by('created_at')
    
    companies = CompanyProfile.objects.filter(workspace=workspace)
    
    context = {
        'workspace': workspace,
        'chat_history': chat_history,
        'companies': companies
    }
    
    return render(request, 'chat.html', context)

@login_required
@csrf_exempt
def chat_message(request, workspace_id):
    """API endpoint for sending/receiving chat messages"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Initialize the chatbot
            chatbot = ChatbotRAG(workspace_id)
            
            # Save the user message
            chatbot.save_message(request.user, message)
            
            # Generate a response
            response = chatbot.generate_response(message)
            
            # Save the assistant message
            chatbot.save_message(request.user, response, is_user_message=False)
            
            return JsonResponse({
                'status': 'success',
                'response': response
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@login_required
def market_trends(request):
    """View market trends"""
    # Get filter parameters
    industry_filter = request.GET.get('industry', '')
    impact_filter = request.GET.get('impact', '1')
    
    # Start with all trends
    trends = MarketTrend.objects.all()
    
    # Apply filters
    if industry_filter:
        trends = trends.filter(industry__icontains=industry_filter)
    
    if impact_filter:
        try:
            impact_level = int(impact_filter)
            trends = trends.filter(impact_level__gte=impact_level)
        except ValueError:
            pass
    
    # Sort by date and impact level
    trends = trends.order_by('-start_date', '-impact_level')
    
    # Get unique industries for the filter dropdown
    all_industries = MarketTrend.objects.values_list('industry', flat=True).distinct()
    
    context = {
        'trends': trends,
        'industries': all_industries,
        'selected_industry': industry_filter,
        'selected_impact': int(impact_filter) if impact_filter.isdigit() else 1
    }
    
    return render(request, 'market_trends.html', context)

@login_required
def add_market_trend(request):
    """Add a market trend"""
    if request.method == 'POST':
        industry = request.POST.get('industry')
        trend_name = request.POST.get('trend_name')
        description = request.POST.get('description')
        impact_level = request.POST.get('impact_level', 3)
        start_date = request.POST.get('start_date')
        
        trend = MarketTrend(
            industry=industry,
            trend_name=trend_name,
            description=description,
            impact_level=impact_level,
            start_date=start_date
        )
        trend.save()
        
        messages.success(request, f"Added trend: {trend_name}")
        return redirect('market_trends')
        
    return render(request, 'add_market_trend.html')