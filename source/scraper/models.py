from django.db import models


class News(models.Model):
    COUNTRY_CHOICES = [
        ('ba', 'Bosnia and Herzegovina'),
        ('hr', 'Croatia'),
        ('rs', 'Serbia'),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField()
    post_time = models.DateTimeField(blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True, null=True)
    url = models.URLField(max_length=500)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"
