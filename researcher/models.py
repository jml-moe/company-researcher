from django.db import models
from django.contrib.auth.models import User
from core.utils import generate_id
from django.utils import timezone

class Workspace(models.Model):
    id = models.CharField(max_length=24, primary_key=True, default=generate_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspaces')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_companies_count(self):
        return self.companies.count()
    
    @classmethod
    def get_default_workspace(cls):
        # Get or create a default workspace for migration purposes
        user, _ = User.objects.get_or_create(
            username='default_user',
            defaults={'email': 'default@example.com'}
        )
        workspace, _ = cls.objects.get_or_create(
            name='Default Workspace',
            defaults={'user': user}
        )
        return workspace.id

class CompanyProfile(models.Model):
    id = models.CharField(max_length=24, primary_key=True, default=generate_id)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='companies', default=Workspace.get_default_workspace)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True, null=True)
    profile_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Company Enrichment Data
    founded_year = models.IntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=255, null=True, blank=True)
    employee_count = models.CharField(max_length=50, null=True, blank=True)
    company_website = models.URLField(null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    crunchbase_url = models.URLField(null=True, blank=True)
    
    # Financial Data
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    annual_revenue = models.CharField(max_length=100, null=True, blank=True)
    funding_total = models.CharField(max_length=100, null=True, blank=True)
    stock_symbol = models.CharField(max_length=20, null=True, blank=True)
    
    # Investment Scoring (1-5)
    financial_health_score = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    business_risk_score = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    growth_potential_score = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    industry_position_score = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    external_trends_score = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    overall_score = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    
    # Insights from AI
    financial_health_insight = models.TextField(blank=True, null=True)
    business_risk_insight = models.TextField(blank=True, null=True)
    growth_potential_insight = models.TextField(blank=True, null=True)
    industry_position_insight = models.TextField(blank=True, null=True)
    external_trends_insight = models.TextField(blank=True, null=True)
    overall_insight = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.company_name
    
    def calculate_overall_score(self):
        scores = [
            self.financial_health_score,
            self.business_risk_score,
            self.growth_potential_score,
            self.industry_position_score,
            self.external_trends_score
        ]
        if all(scores):
            self.overall_score = sum(scores) / len(scores)
            self.save(update_fields=['overall_score'])
        return self.overall_score

class ExecutiveTeam(models.Model):
    id = models.CharField(max_length=24, primary_key=True, default=generate_id)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='executives')
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    linkedin_url = models.URLField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_image_url = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.position} at {self.company.company_name}"

class CompetitorRelation(models.Model):
    id = models.CharField(max_length=24, primary_key=True, default=generate_id)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='competitors')
    competitor_name = models.CharField(max_length=255)
    competitor_website = models.URLField(null=True, blank=True)
    relationship_strength = models.IntegerField(default=1)  # 1-5 scale
    competitive_areas = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.company.company_name} - {self.competitor_name}"

class FundingRound(models.Model):
    id = models.CharField(max_length=24, primary_key=True, default=generate_id)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='funding_rounds')
    round_type = models.CharField(max_length=50)  # Seed, Series A, etc.
    amount = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    lead_investors = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.company.company_name} - {self.round_type} ({self.date})"

class MarketTrend(models.Model):
    id = models.CharField(max_length=24, primary_key=True, default=generate_id)
    industry = models.CharField(max_length=255)
    trend_name = models.CharField(max_length=255)
    description = models.TextField()
    impact_level = models.IntegerField(default=3)  # 1-5 scale
    start_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.trend_name} in {self.industry}"

class CompanyDocument(models.Model):
    id = models.CharField(max_length=24, primary_key=True, default=generate_id)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50)  # annual_report, financial_statement, etc.
    file = models.FileField(upload_to='company_documents/')
    extracted_text = models.TextField(blank=True, null=True)
    key_points = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company.company_name} - {self.title}"

class ChatMessage(models.Model):
    id = models.CharField(max_length=24, primary_key=True, default=generate_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    is_user_message = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{'User' if self.is_user_message else 'AI'}: {self.message[:30]}..."
