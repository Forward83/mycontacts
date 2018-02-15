from rest_framework import serializers
from contacts.models import Contact


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Contact
        fields = ('url', 'id', 'owner', 'firstname', 'secondname', 'lastname', 'mobile', 'personal_phone',
                  'address', 'email', 'star')
