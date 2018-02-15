from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .permissions import IsOwner
from .serializers import ContactSerializer
from contacts.models import Contact


# Create your views here.
@api_view(['GET'])
def root_api(request, format=None):
    return Response({
        'contacts': reverse('contact-list', request=request, format=format),
    })


class ContactList(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Contact.objects.filter(owner=user)


class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


