from datetime import timedelta
from ipaddress import ip_address
from math import ceil

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import SubmissionLimit


def client_address(request):
    address = request.META.get("REMOTE_ADDR", "")
    if settings.ON_VERCEL:
        address = request.META.get("HTTP_X_VERCEL_FORWARDED_FOR") or address
    try:
        return ip_address(address.split(",")[0].strip()).compressed
    except ValueError:
        return "unknown"


def reserve_submission(request, scope, *, limit, window):
    now = timezone.now()
    expires_at = now + timedelta(seconds=window)
    address = client_address(request)
    keys = [
        salted_hmac(
            "portfolio.submission-slot",
            f"{scope}:{address}:{index}",
            algorithm="sha256",
        ).hexdigest()
        for index in range(limit)
    ]

    SubmissionLimit.objects.filter(expires_at__lte=now).delete()
    reservations = dict(
        SubmissionLimit.objects.filter(key__in=keys).values_list("key", "expires_at")
    )

    for key in keys:
        if key in reservations:
            continue

        slot, created = SubmissionLimit.objects.get_or_create(
            key=key,
            defaults={"count": 1, "expires_at": expires_at},
        )
        if created:
            return slot, 0
        reservations[key] = slot.expires_at

    earliest = min(reservations.values())
    return None, max(1, ceil((earliest - now).total_seconds()))
