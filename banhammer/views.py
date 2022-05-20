import urllib
import urllib.parse

import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import AccountSettings, BanHammer


def auth_twitch(request, *args, **kwargs):

    code = request.GET.get('code')
    account = AccountSettings.objects.first()

    redirect_uri = request.scheme + '://' + request.get_host() + request.path

    if not code:
        url = r'https://id.twitch.tv/oauth2/authorize'
        data = dict(
            client_id=account.client_id,
            redirect_uri=redirect_uri,
            response_type='code',
            scope=account.get_scopes(),
        )

        redirect_url = url + '?' + urllib.parse.urlencode(data)
        print(redirect_uri)
        print(redirect_url)
        return redirect(redirect_url)

    else:
        url = r'https://id.twitch.tv/oauth2/token'

        data = dict(
            client_id=account.client_id,
            client_secret=account.secret_key,
            code=code,
            grant_type='authorization_code',
            redirect_uri=redirect_uri,
        )

        response = requests.post(
            url,
            data=data
        )

        res = {}
        if response.status_code == 200:
            res = response.json()

            account.access_token = res['access_token']
            account.expires_in = res['expires_in']
            account.refresh_token = res['refresh_token']
            account.token_type = res['token_type']

            account.save()

        return JsonResponse(data=res)


def connect_events(request, *args, **kwargs):
    """
    POST https://api.twitch.tv/helix/eventsub/subscriptions
    """
    event_type = 'channel.update'
    account = AccountSettings.objects.first()
    data = {
        "type": f"{event_type}",
        "version": "1",
        "condition": {
            "broadcaster_user_id": f"{account.channel_id}"
        },
        "transport": {
            "method": "webhook",
            "callback": f"{request.scheme}://{request.get_host()}/twitch/event/callback/",
            "secret": f"s3cRe7"
        }
    }

    print(data['transport'])

    print(data)

    headers = {
            'Accept': 'application/json',
            'Client-ID': account.client_id,
            'Authorization': f'Bearer {account.app_token}',
    }

    response = requests.post('https://api.twitch.tv/helix/eventsub/subscriptions', data=data, headers=headers)
    print(response.text)

    return JsonResponse(data={'res': response.text})


def connect_events_callback(request, *args, **kwargs):
    """
    POST https://api.twitch.tv/helix/eventsub/subscriptions
    """
    a = 1
    return JsonResponse(data={})



def banhammer_ban(request, *args, **kwargs):

    banhammer_id = request.GET.get('banhammer')
    bh = BanHammer.objects.get(id=banhammer_id)

    account = AccountSettings.objects.first()
    headers = {
            'Accept': 'application/json',
            'Client-ID': account.client_id,
            'Authorization': f'Bearer {account.access_token}',
    }

    def get_user_id(username):
        # GET channel id
        url = 'https://api.twitch.tv/helix/users'
        data = dict(login=username)
        querystring = '&'.join([f'{x}={y}' for x, y  in data.items()])
        response = requests.get(f'{url}?{querystring}', headers=headers)
        print(response.json())
        if response.status_code != 200:
            raise ValueError(response.status_code)

        channel_id = response.json().get('data')[0].get('id')
        return channel_id

    who_ban = get_user_id(account.username)
    where_ban = get_user_id(bh.channel)

    ban_url = 'https://api.twitch.tv/helix/moderation/bans'

    for ban_variant in bh.user.variants.all():
        try:
            ban_target = get_user_id(ban_variant.username)
        except IndexError:
            continue
        data = dict(
            broadcaster_id=where_ban,
            moderator_id=who_ban,
            user_id=ban_target,
            end_time=None,
        )
        response = requests.post(ban_url, data=data, headers=headers)
        print('Banned')
        print(response.json())