from django.db import models

# Create your models here.


class Review(models.Model):
    RATINGS_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )

    name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=RATINGS_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_rating_display()}"
