from django.urls import path
from .views import (
    IndexView, 
    WorkspaceListView, 
    WorkspaceCreateView,
    WorkspaceDetailView,
    DeleteWorkspaceView,
    ResearchCompanyView,
    CompanyDetailView,
    CompareCompaniesView,
    UploadDocumentView,
    DeleteCompanyView,
    chat_view,
    chat_message,
    market_trends,
    add_market_trend
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    
    # Workspace routes
    path("workspaces/", WorkspaceListView.as_view(), name="workspace_list"),
    path("workspaces/create/", WorkspaceCreateView.as_view(), name="workspace_create"),
    path("workspaces/<str:workspace_id>/", WorkspaceDetailView.as_view(), name="workspace_detail"),
    path("workspaces/<str:workspace_id>/delete/", DeleteWorkspaceView.as_view(), name="workspace_delete"),
    
    # Company research routes
    path("workspaces/<str:workspace_id>/research/", ResearchCompanyView.as_view(), name="research_company"),
    path("workspaces/<str:workspace_id>/company/<str:profile_id>/", CompanyDetailView.as_view(), name="company_detail"),
    path("workspaces/<str:workspace_id>/company/<str:profile_id>/delete/", DeleteCompanyView.as_view(), name="delete_company"),
    
    # Document management
    path("workspaces/<str:workspace_id>/company/<str:profile_id>/upload-document/", UploadDocumentView.as_view(), name="upload_document"),
    
    # Comparison
    path("workspaces/<str:workspace_id>/compare/", CompareCompaniesView.as_view(), name="compare_companies"),
    
    # Chat URLs
    path("workspaces/<str:workspace_id>/chat/", chat_view, name="chat_view"),
    path("workspaces/<str:workspace_id>/chat/message/", chat_message, name="chat_message"),
    
    # Market Intelligence URLs
    path("market-trends/", market_trends, name="market_trends"),
    path("market-trends/add/", add_market_trend, name="add_market_trend"),
]