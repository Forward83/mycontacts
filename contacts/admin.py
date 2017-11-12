from django.contrib import admin
from django.contrib.auth.models import User
from .models import Contact, ContactPhoto, Dublicate
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from django.forms import ValidationError
import re


class ContactResource(resources.ModelResource):
    owner = fields.Field(
        column_name='owner',
        attribute='owner',
        widget=ForeignKeyWidget(User)
    )
    
    class Meta:
        model = Contact
        exclude = ('owner',)

    def for_delete(self, row, instance):
        mobile = str(row['mobile'])
        macth = re.match(r'^\+380\([0-9]{2}\)[0-9]{7}$', mobile)
        if not macth:
            print('Error in phone number')
            raise ValidationError("Phone number must be entered in the format: '+380(67)9999999'. Up to 15 digits allowed. "
                                  "Error in row with id = %s" % row['id'], code='invalid_mobile'
                                  )
        return False


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
admin.site.register(Dublicate)

