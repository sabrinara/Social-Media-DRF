from django.urls import path
from .views import (PopularReviewsList, ReviewDetail,
                    AddReview, AllReviewsList)

urlpatterns = [
    path('', PopularReviewsList.as_view(), name='popular_reviews'),
    path('<int:pk>/', ReviewDetail.as_view(), name='review_detail'),
    path('add/', AddReview.as_view(), name='add_review'),
    path('all/', AllReviewsList.as_view(), name='all_reviews'),
]
