from django.shortcuts import render
from django.forms.forms import Form
from django.forms.fields import SelectMultiple, CharField, FileField, IntegerField


from ...yt_api import query_maker


class UCForm(Form):
    video_url = CharField()
    period = IntegerField()

def get_likes(request, context):
    if request.method == 'POST':
        form = UCForm(request.POST, request.FILES)
        context['form'] = form

        if form.is_valid():
            video_url = request.POST['video_url']

            users = query_maker.query_video_likes(video_url)

            context['result']['details'] = [u['channelId'] for u in users] 
            context['result']['status'] = True
        else:
            context['result']['status'] = False

    return render(
        request, 'modules/video_likes.html', context
    )
