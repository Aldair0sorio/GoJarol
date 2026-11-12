from django.db import models


class Subject(models.Model):
    slug = models.SlugField(unique=True)
    nombre = models.CharField(max_length=100)
    disponible = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.nombre


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    slug = models.SlugField()
    nombre = models.CharField(max_length=150)
    disponible = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden"]
        unique_together = ("subject", "slug")

    def __str__(self):
        return f"{self.subject.nombre} / {self.nombre}"