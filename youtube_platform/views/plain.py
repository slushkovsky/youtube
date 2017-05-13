from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Plain

from .menu import create_context_from_request
from .modules import ServicePermission


@login_required
def handle_plains(request):
    context = create_context_from_request(request)
    context['disable_page_bg'] = True

    if 'plain' in request.GET:
        plain = request.GET['plain']
        # After purchasing we can add new permission
        plain = Plain.objects.get(id=int(plain))

        print(plain.get_permission())

        request.user.profile.add_perm(plain.get_permission())

        context['result']['status'] = True
        context['result']['details'] = plain.title

    context['plains'] = [
        dict(
            p.dict(),
            disabled=request.user.profile.has_perm(p.get_permission())
        )
        for p in Plain.objects.filter(hidden=False).all()
    ]

    return render(
        request, 'plain.html', context
    )
