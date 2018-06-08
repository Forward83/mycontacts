from rest_framework import serializers
from contacts.models import Contact

class ContactSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # photos = serializers.HyperlinkedIdentityField()

    class Meta:
        model = Contact
        fields = ('url', 'id', 'owner', 'firstname', 'secondname', 'lastname', 'mobile', 'personal_phone',
                  'business_phone', 'company', 'position', 'address', 'email', 'star')
