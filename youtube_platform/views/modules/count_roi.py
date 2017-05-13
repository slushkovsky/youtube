from django.forms import Form, ValidationError
from django.forms import fields
from django.shortcuts import render
from django.http.response import HttpResponseNotFound, HttpResponseRedirect

from ...models import ROILink
from .utils import generate_colors


class ROIForm(Form):
    link = fields.URLField()
    label = fields.CharField()

    def __init__(self, user, data):
        super().__init__(data)
        self.user = user

    def save(self, commit=False):
        if commit:
            if ROILink.objects.filter(
                user=self.user,
                link=self.cleaned_data['link'],
                label=self.cleaned_data['label']
            ).count() > 0:
                raise ValidationError(
                    f"""Ссылка "{self.cleaned_data['link']}" уже зарегистрирована!"""
                )
            ROILink.objects.create(
                user=self.user,
                link=self.cleaned_data['link'],
                label=self.cleaned_data['label']
            )


def count_roi(request, context):
    if request.method == 'POST':
        form = ROIForm(request.user.profile, request.POST)
        if form.is_valid():
            form.save(True)
            context['result']['status'] = True
            context['result']['details'] = {
                'link': form.cleaned_data['link'],
                'label': form.cleaned_data['label']
            }
    else:
        form = ROIForm(request.user.profile, None)

    context['form'] = form
    context['roi_statistic'] = [
        {
            'label': r.label,
            'link': r.link,
            'visits': r.visits,
            'color': color,
            'uuid': r.uuid
        }
        for color, r in zip(
            generate_colors(generate_hex=True),
            ROILink.objects.filter(user=request.user.profile)
        )
    ]

    return render(request, 'modules/count_roi.html', context)


def process_roi(request):
    uuid = request.GET.get('id')
    if uuid is None:
        return HttpResponseNotFound()

    try:
        roi = ROILink.objects.get(uuid=uuid)
        roi.visits += 1
        roi.save()
    except ROILink.DoesNotExist:
        return HttpResponseNotFound()

    print(roi.link)

    return HttpResponseRedirect(roi.link)
