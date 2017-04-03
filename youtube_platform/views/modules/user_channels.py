from django.shortcuts import render
from django.forms.forms import Form
from django.forms.fields import SelectMultiple, FileField


from ...yt_api import query_maker


SOCIALS_ENUM = [
    'VK', 'Facebook', 'Twitter',
    'Instagram', 'Youtube', 'Odnoklassniki',
]


class UCForm(Form):
    social = SelectMultiple(choices=SOCIALS_ENUM)
    links = FileField()


def users_channels(request, context):
    if request.method == 'POST':
        form = UCForm(request.POST, request.FILES)
        context['form'] = form
        if form.is_valid():
            social = request.POST['social']
            file = request.FILES['links']

            social_links = [
                l.decode().strip() for l in file.readlines()
            ]
            channels = query_maker.query_users_channels(social, social_links)
            getattr(request, 'add_to_params')['links'] = social_links

            context['result']['details'] = channels
            context['result']['status'] = True
        else:
            context['result']['status'] = False

    return render(
        request, 'modules/user_channels.html', context
    )
