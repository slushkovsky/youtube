import json

from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from ..models import Feature, FeatureUsage

from .menu import create_context_from_request
from .modules import FEATURES


@login_required
def entry_point(request, feature=None, **kwargs):
    feature = request.GET.get('feature') or feature

    if feature not in FEATURES:
        return HttpResponseNotFound(f'Feature {feature} not found.')

    permission, handler = FEATURES[feature]
    if not request.user.profile.has_perm(permission):
        return HttpResponseForbidden(
            f'Feature {feature} not allowed on your plan.'
        )

    context = create_context_from_request(request)

    if request.method == 'POST':
        additional_params = {}
        setattr(request, 'add_to_params', additional_params)
        res = handler(request, context, **kwargs)

        if context['result']['status']:
            additional_params.update(request.POST)
            FeatureUsage.objects.create(
                feature=Feature.get_by_name(feature),
                parameters=json.dumps(additional_params),
                user=request.user.profile
            )

        return res
    else:
        return handler(request, context, **kwargs)
