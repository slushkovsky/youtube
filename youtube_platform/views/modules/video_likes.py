from django.shortcuts import render
from django.forms.forms import Form
from django.forms.fields import SelectMultiple, FileField


from ...yt_api import query_maker


class UCForm(Form):
    video_url = CharField()

def users_channels(request, context):
    if request.method == 'POST':
        form = UCForm(request.POST, request.FILES)
        context['form'] = formi

        if form.is_valid():
            video_url = request.POST['video_url']

            likes_count = query_maker.query_video_likes(video_url)

            context['result']['details'] = likes_count 
            context['result']['status'] = True
        else:
            context['result']['status'] = False

    return render(
        request, 'modules/video_likes.html', context
    )
