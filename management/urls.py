# Add to your urlpatterns
path('complaint/view/<str:complaint_id>/', views.view_complaint, name='view_complaint'),