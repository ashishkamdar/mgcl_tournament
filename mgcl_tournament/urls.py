from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from tournament import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- ADMIN ---
    path('admin/', admin.site.urls),
    
    # --- AUTHENTICATION & GATEWAY ---
    # This matches the names used in your gateway and custom_logout view
    path('login-selection/', views.login_selection, name='login_selection'),
    path('login/', auth_views.LoginView.as_view(template_name='tournament/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # --- MAIN PAGES ---
    path('', views.fixtures, name='home'), 
    path('fixtures/', views.fixtures, name='fixtures'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('big-screen/', views.big_screen, name='big_screen'), 

    # --- CAPTAIN'S PORTAL ---
    # Fixed these paths to ensure Reverse Match works for captain_dashboard
    path('captain-dashboard/', views.captain_dashboard, name='captain_dashboard'),
    path('match/<int:match_id>/select-squad/', views.select_squad, name='select_squad'),

    # --- SCORING & DATA ---
    path('score/<int:match_id>/', views.score_entry, name='score_entry'),
    path('leaderboard/data/', views.leaderboard_data, name='leaderboard_data'),
] 

# Essential for serving the MGCL logo and team icons
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)