from rest_framework import generics
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


class PopularReviewsList(generics.ListAPIView):
    queryset = Review.objects.order_by('-rating')[:5]
    serializer_class = ReviewSerializer


class AllReviewsList(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class ReviewDetail(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class AddReview(generics.CreateAPIView):
    serializer_class = ReviewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
