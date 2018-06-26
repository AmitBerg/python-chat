from social_django.models import UserSocialAuth


def user_social_connection(request):
    try:
        social_user = UserSocialAuth.objects.get(user=request.user)
    except Exception:
        return {}
    provider = social_user.provider
    provider = 'Twitter' if provider == 'twitter' else 'Google'
    return {"social_net": provider}
