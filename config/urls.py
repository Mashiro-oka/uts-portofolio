from django.urls import path

from portfolio import views

urlpatterns = [
    path("", views.home, name="home"),
    path("proyek/<int:pk>/", views.project_detail, name="project_detail"),
    path("proyek/<int:pk>/gambar/", views.project_image, name="project_image"),
    path("admin/", views.dashboard, name="dashboard"),
    path("admin/login/", views.AdminLogin.as_view(), name="admin_login"),
    path("admin/logout/", views.admin_logout, name="admin_logout"),
    path("admin/proyek/baru/", views.project_editor, name="project_create"),
    path("admin/proyek/<int:pk>/edit/", views.project_editor, name="project_edit"),
    path("admin/proyek/<int:pk>/hapus/", views.project_delete, name="project_delete"),
    path("admin/pesan/", views.inbox, name="inbox"),
]
