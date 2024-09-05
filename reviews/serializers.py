from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.ChoiceField(choices=Review.RATINGS_CHOICES)

    class Meta:
        model = Review
        fields = ['id', 'name', 'rating', 'message', 'created_at']
