from django.db import models

TYPE_RESPONSES = (("greeting_keyword", "Greeting Keyword"),
                  ("greeting_response", "Greeting Response"),
                  ("none_response", "None Response"),
                  ("comments_about_self", "Comment about self"),
                  ("self_verbs_with_noun_caps_plural", "Self verbs with noun caps plural"),
                  ("self_verbs_with_noun_lower", "Self verbs with noun lower"),
                  ("self_verbs_with_adjective", "Self verbs with adjective"))


class ResponseManger(models.Manager):

    def greeting_keywords(self):
        return self.filter(type="greeting_keyword")

    def greeting_responses(self):
        return self.filter(type="greeting_response")

    def none_responses(self):
        return self.filter(type="none_response")

    def comments_about_self(self):
        return self.filter(type="comments_about_self")

    def self_verbs_with_noun_caps_plural(self):
        return self.filter(type="self_verbs_with_noun_caps_plural")

    def self_verbs_with_noun_lower(self):
        return self.filter(type="self_verbs_with_noun_lower")

    def self_verbs_with_adjective(self):
        return self.filter(type="self_verbs_with_adjective")


class Response(models.Model):
    type = models.CharField(max_length=64, choices=TYPE_RESPONSES)
    text = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    objects = ResponseManger()

    def __str__(self):
        return self.text


def random_model(queryset):
    return queryset.order_by("?").first()
