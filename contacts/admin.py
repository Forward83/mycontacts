from django.contrib import admin
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Contact, ContactPhoto, Dublicate
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from django.forms import ValidationError
from django.core.files.storage import default_storage
import re, os


def path_to_archieve(base_dir):
    for base, dirnames, filenames in os.walk(base_dir):
        if dirnames:
            base_dir = os.path.join(base_dir, dirnames[0])
            path_to_archieve(base_dir)
        else:
            return base_dir


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

    def save_instance(self, instance, using_transactions=None, dry_run=False):
        self.before_save_instance(instance, using_transactions, dry_run)
        if dry_run:
            pass
        else:
            original_id = instance.id
            try:  # If user didn't upload any photo previously
                base_path = '{}/tmp'.format(instance.owner.id)
                path_to_folder = path_to_archieve(base_path)
                path_to_photo = os.path.join(path_to_folder, '{}.png'.format(instance.id))
            except TypeError:
                path_to_photo = '{}/tmp/{}.png'.format(instance.owner.id, instance.id)
            if instance.id and default_storage.exists(path_to_photo):
                instance.id = None
                instance.save()
                with default_storage.open(path_to_photo, 'rb') as fcontent:
                    fname = '{}.png'.format(original_id)
                    photo_field = SimpleUploadedFile(fname, fcontent.read(), 'image/png')
                    c = ContactPhoto.objects.create(contact=instance)
                    # c = ContactPhoto(contact=instance)
                    c.photo = photo_field
                    c.save()
            else:
                instance.id = None
                instance.save()
        self.after_save_instance(instance, using_transactions, dry_run)

class ContactAdmin(ImportExportModelAdmin):
    resource_class = ContactResource

#for exporting photo files as zip
class ContactPhotoResource(resources.ModelResource):
    class Meta:
        model = ContactPhoto
        # fields = ('contact', 'thumbnail')
        fields = ('thumbnail')

# Register your models here.

# admin.site.register(Contact)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactPhoto)
admin.site.register(Dublicate)

