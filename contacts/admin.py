from django.contrib import admin
from .models import Contact, ContactPhoto
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact
        exclude = ('id', 'owner',)

class ContactAdmin(ImportExportModelAdmin):
    resource_class = ContactResource

#for exporting photo files as zip
class ContactPhotoResource(resources.ModelResource):
    class Meta:
        model = Contact
        fields = ('photo',)

# Register your models here.

# admin.site.register(Contact)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactPhoto)

