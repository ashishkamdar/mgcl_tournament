from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from tournament import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- ROOT REDIRECT ---
    # This ensures that mgcl.areakpi.in leads directly to your branding/gateway page
    path('', views.login_selection, name='login_selection'), 
    
    # --- ADMIN ---
    path('admin/', admin.site.urls),
    
    # --- AUTHENTICATION & GATEWAY ---
    # Standardizing login paths for the @login_required decorator to find
    path('login-selection/', views.login_selection, name='login_selection'),
    path('login/', auth_views.LoginView.as_view(template_name='tournament/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # --- MAIN PAGES ---
    path('fixtures/', views.fixtures, name='fixtures'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('big-screen/', views.big_screen, name='big_screen'), 

    # --- CAPTAIN'S PORTAL ---
    path('captain-dashboard/', views.captain_dashboard, name='captain_dashboard'),
    path('match/<int:match_id>/select-squad/', views.select_squad, name='select_squad'),

    # --- SCORING & DATA ---
    path('score/<int:match_id>/', views.score_entry, name='score_entry'),
    path('leaderboard/data/', views.leaderboard_data, name='leaderboard_data'),
] 

# Serve media files (logo/icons) in local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)