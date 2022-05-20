import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _



class BanableUser(models.Model):

    class Meta:
        verbose_name = _('bannable user')
        verbose_name_plural = _('bannable users')

    username_verbose = models.CharField(
        verbose_name=_('readable username'),
        max_length=255,
        db_index=True,
    )

    def __str__(self):
        return self.username_verbose


class BanableUserVariant(models.Model):

    class Meta:
        verbose_name = _('bannable user variant')
        verbose_name_plural = _('bannable user variants')

        ordering = ['username']

    bannable_user = models.ForeignKey(
        to=BanableUser,
        on_delete=models.CASCADE,
        related_name='variants',
    )

    username = models.CharField(
        verbose_name=_('username variant'),
        max_length=255,
        db_index=True,
    )

    def __str__(self):
        return self.username



class AccountSettings(models.Model):

    class Meta:
        verbose_name = _('account settings')
        verbose_name_plural = _('accounts settings')

    client_id = models.CharField(
        verbose_name=_('client id'),
        max_length=255,
    )

    secret_key = models.CharField(
        verbose_name=_('secret key'),
        max_length=255,
    )

    access_token = models.CharField(
        verbose_name=_('access token'),
        max_length=255,
        blank=True,
        null=True,
    )

    expires_in = models.IntegerField(
        verbose_name=_('expires in'),
        blank=True,
        null=True,
    )


    refresh_token = models.CharField(
        verbose_name=_('refresh token'),
        max_length=255,
        blank=True,
        null=True,
    )

    token_type = models.CharField(
        verbose_name=_('token type'),
        max_length=255,
        blank=True,
        null=True,
    )

    channel_id = models.IntegerField(
        verbose_name=_('channel id'),
        blank=True,
        null=True,
    )

    username = models.CharField(
        verbose_name=_('username'),
        max_length=255,
    )

    app_token = models.CharField(
        verbose_name=_('user token'),
        max_length=255,
        blank=True,
        null=True,
    )

    def get_channel_data(self):
        headers = {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': self.client_id,
            'Authorization': f'OAuth {self.access_token}',
        }
        response = requests.get('https://api.twitch.tv/kraken/channel', headers=headers)
        if response:
            return response.json()

    def get_app_token_data(self):
        # headers = {
        #     'Accept': 'application/vnd.twitchtv.v5+json',
        #     'Client-ID': self.client_id,
        #     'Authorization': f'OAuth {self.access_token}',
        # }
        data = {
            'client_id': self.client_id,
            'client_secret': self.secret_key,
            'grant_type': 'client_credentials',
            'scope': self.get_scopes()
        }
        response = requests.post(
            'https://id.twitch.tv/oauth2/token',
            # headers=headers,
            data=data,
        )
        return response
        if response:
            return response.json()


    def load_channel_id(self):
        res = self.get_channel_data()
        if res:
            self.channel_id = res['_id']
            self.save()

    def get_scopes(self):
        return ' '.join([
            'channel_subscriptions',
            'channel_commercial',
            'channel_editor',
            'user_follows_edit',
            'channel_read',
            'user_read',
            'user_blocks_read',
            'user_blocks_edit',

            "analytics:read:extensions",
            "analytics:read:games",
            "bits:read",
            "channel:edit:commercial",
            "channel:manage:broadcast",
            "channel:manage:extensions",
            "channel:manage:polls",
            "channel:manage:predictions",
            "channel:manage:redemptions",
            "channel:manage:videos",
            "channel:read:editors",
            "channel:read:hype_train",
            "channel:read:polls",
            "channel:read:predictions",
            "channel:read:redemptions",
            "channel:read:stream_key",
            "channel:read:subscriptions",
            "clips:edit",
            "moderation:read",
            "moderator:manage:automod",
            "user:edit",
            "user:edit:follows",
            "user:manage:blocked_users",
            "user:read:blocked_users",
            "user:read:broadcast",
            "user:read:follows",
            "user:read:subscriptions",

            'moderator:manage:banned_users'
        ])

    def get_topics(self):
        if not self.channel_id:
            raise Exception('Have not channel_id')

        return [
            f'{x}.{self.channel_id}' for x in [
                'channel-bits-events-v1',
                'channel-bits-events-v2',
                'channel-bits-badge-unlocks',
                'channel-points-channel-v1',
                'channel-subscribe-events-v1',
            ]
        ]


class BanHammer(models.Model):

    class Meta:
        verbose_name = _('ban hammer')

    user = models.ForeignKey(
        to=BanableUser,
        on_delete=models.PROTECT,
    )

    ban = models.BooleanField(
        default=True,
        blank=True,
    )

    channel = models.CharField(
        max_length=255,
    )

