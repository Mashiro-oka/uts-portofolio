from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.html import format_html
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .forms import AdminAuthenticationForm, ContactForm, ProjectForm
from .models import ContactMessage, Project, ProjectImage, SubmissionLimit
from .rate_limits import reserve_submission

admin_required = user_passes_test(lambda user: user.is_active and user.is_superuser)


def projects_with_images():
    images = ProjectImage.objects.filter(project_id=OuterRef("pk"))
    return Project.objects.annotate(has_image=Exists(images))


@require_http_methods(["GET", "POST"])
def home(request):
    form = ContactForm(request.POST if request.method == "POST" else None)
    wait = 0
    if request.method == "POST":
        _, wait = reserve_submission(request, "contact", limit=8, window=60)
        if wait:
            messages.error(request, "Terlalu banyak pengiriman. Tunggu sebentar, lalu coba lagi.")
        elif form.is_valid():
            if not form.cleaned_data["website"]:
                form.save()
            messages.success(request, "Pesan Anda sudah terkirim.")
            return redirect(reverse("home") + "#contact")
    published_projects = projects_with_images().filter(published=True)
    projects = Paginator(published_projects, 8).get_page(request.GET.get("page"))
    response = render(
        request,
        "home.html",
        {"projects": projects, "form": form},
        status=429 if wait else 200,
    )
    if wait:
        response.headers["Retry-After"] = str(wait)
    return response


def project_detail(request, pk):
    project = get_object_or_404(projects_with_images(), pk=pk, published=True)
    return render(request, "home.html", {"project": project})


@never_cache
def project_image(request, pk):
    images = ProjectImage.objects.filter(project_id=pk)
    if not request.user.is_superuser:
        images = images.filter(project__published=True)
    image = get_object_or_404(images)
    return HttpResponse(bytes(image.content), content_type=image.content_type)


class AdminLogin(LoginView):
    template_name = "login.html"
    authentication_form = AdminAuthenticationForm
    next_page = reverse_lazy("dashboard")

    def post(self, request, *args, **kwargs):
        self.login_slot, wait = reserve_submission(
            request, "admin-login-failures", limit=5, window=600
        )
        if not wait:
            return super().post(request, *args, **kwargs)
        context = self.get_context_data(
            form=self.get_form_class()(request=request),
            rate_limit_message=format_html(
                "Terdeteksi bukan <strong>{}</strong>. Dilarang masuk! 🍙",
                "Onigirya",
            ),
        )
        response = self.render_to_response(context, status=429)
        response.headers["Retry-After"] = str(wait)
        return response

    def form_valid(self, form):
        response = super().form_valid(form)
        SubmissionLimit.objects.filter(
            pk=self.login_slot.pk,
            expires_at=self.login_slot.expires_at,
        ).delete()
        return response

    def get_success_url(self):
        return self.next_page


@never_cache
@admin_required
def dashboard(request):
    projects = Paginator(projects_with_images(), 15).get_page(request.GET.get("page"))
    return render(request, "dashboard.html", {"projects": projects, "heading": "Dashboard proyek"})


@never_cache
@admin_required
def inbox(request):
    items = Paginator(ContactMessage.objects.all(), 15).get_page(request.GET.get("page"))
    return render(
        request,
        "dashboard.html",
        {"panel": "inbox", "items": items, "heading": "Pesan masuk"},
    )


@never_cache
@admin_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def project_editor(request, pk=None):
    queryset = Project.objects.select_for_update() if request.method == "POST" else Project.objects.all()
    project = get_object_or_404(queryset, pk=pk) if pk else None
    has_image = bool(project and ProjectImage.objects.filter(project=project).exists())
    form = ProjectForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=project,
    )
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        if upload := form.cleaned_data["image_upload"]:
            content, content_type = upload
            ProjectImage.objects.update_or_create(
                project=saved,
                defaults={"content": content, "content_type": content_type},
            )
        elif form.cleaned_data["remove_image"]:
            ProjectImage.objects.filter(project=saved).delete()
        messages.success(request, "Proyek disimpan.")
        return redirect("dashboard")
    return render(
        request,
        "dashboard.html",
        {
            "panel": "editor",
            "heading": "Edit proyek" if project else "Tambah proyek",
            "form": form,
            "project": project,
            "has_image": has_image,
        },
    )


@never_cache
@admin_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def project_delete(request, pk):
    queryset = Project.objects.select_for_update() if request.method == "POST" else Project.objects.all()
    project = get_object_or_404(queryset, pk=pk)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek dihapus.")
        return redirect("dashboard")
    return render(
        request,
        "dashboard.html",
        {
            "panel": "delete",
            "heading": "Hapus proyek",
            "project": project,
        },
    )


@require_POST
def admin_logout(request):
    logout(request)
    return redirect("admin_login")
