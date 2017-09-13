from django.contrib import admin
from django.contrib.auth.models import User
from .models import Contact, ContactPhoto
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin


class ContactResource(resources.ModelResource):
    owner = fields.Field(
        column_name='owner',
        attribute='owner',
        widget=ForeignKeyWidget(User)
    )
    
    class Meta:
        model = Contact
        exclude = ('owner',)

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

