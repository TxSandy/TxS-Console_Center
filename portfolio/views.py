from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .models import ProjectUpload, ContactMessage
from .serializers import ProjectUploadSerializer, ContactMessageSerializer

class StandardUserThrottle(UserRateThrottle):
    rate = '10/min'


class ProjectUploadListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectUploadSerializer
    throttle_classes = [StandardUserThrottle]
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'desc', 'tags__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return ProjectUpload.objects.select_related('author').prefetch_related('tags').only(
            'id', 'author__username', 'title', 'slug', 'image', 'created_at', 'is_published'
        ).filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ProjectUploadDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectUploadSerializer
    throttle_classes = [StandardUserThrottle]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return ProjectUpload.objects.select_related('author').prefetch_related('tags')


class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    throttle_classes = [StandardUserThrottle]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Optionally, you can add custom response or perform other actions (e.g., send email)
        return response


class ContactMessageListView(generics.ListAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdminUser]  # Restrict access to admin users or implement custom permission
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'message']
    ordering = ['-submitted_at']
