from tournament import views

urlpatterns += [
    path("leaderboard/", views.leaderboard),
    path("fixtures/", views.fixtures),
]
