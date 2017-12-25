from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
import imghdr

#Validator for mobile number
mobile_regex = RegexValidator(regex=r'^\+380\([0-9]{2}\)[0-9]{7}$',
                              message="Phone number must be entered in the format: '+380(67)9999999'. Up to 15 digits allowed.",
                              code='invalid_mobile')

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
        
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save() 
    
class Contact(models.Model):
    owner = models.ForeignKey(User)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=40, blank=True, null=True)
    secondname = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=15, validators=[mobile_regex])
    personal_phone = models.CharField(max_length=15, blank=True, null=True)
    business_phone = models.CharField(max_length=4, blank=True, null=True)
    company = models.CharField(max_length=15, blank=True, null=True)
    position = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    star = models.BooleanField(default=False)

    # var for tracking change in photo field to make decision regarding create_thumbnail

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname)

    def delete(self, using=None, keep_parents=False):
        photos = self.contactphoto_set.all()
        if photos:
            for photo in photos:
                if photo.photo:
                    default_storage.delete(photo.photo.name)
                    # photo.photo.delete()
                    # photo.thumbnail.delete()
        super(Contact, self).delete()

class Dublicate(models.Model):
    contact_id = models.ForeignKey(Contact)
    count = models.SmallIntegerField()

    def __str__(self):
        return '%s %s %s' % (self.contact_id.firstname, self.contact_id.secondname, self.contact_id.mobile)

#Return separate path directory for each user
def user_directory_path(instance, filename):
    return '{0}/{1}'.format(instance.contact.owner_id, filename)


class ContactPhoto(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=user_directory_path, blank=True, null=True, editable=False)
    load_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-load_date']

    __original_photo = None

    def __init__(self, *args, **kwargs):
        super(ContactPhoto, self).__init__(*args, **kwargs)
        self.__original_photo = self.photo

    def __str__(self):
        return "Contact: %s %s %s" % (self.contact.firstname, self.contact.lastname, self.thumbnail.name)

    def create_thumbnail(self):
        if not self.photo:
            return
        from PIL import Image
        from io import BytesIO
        from contact.settings import THUMB_SIZE
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        thumb_extension = os.path.splitext(self.photo.name)[1].lower()
        if thumb_extension in ['.jpg', '.jpeg']:
            PIL_TYPE = 'JPEG'
        elif thumb_extension == '.gif':
            PIL_TYPE = 'GIF'
        elif thumb_extension == '.png':
            PIL_TYPE = 'PNG'

        img = Image.open(BytesIO(self.photo.read()))
        img.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
        tmp_handle = BytesIO()
        img.save(tmp_handle, PIL_TYPE)
        tmp_handle.seek(0)
        suf = SimpleUploadedFile(os.path.split(self.photo.name)[-1], tmp_handle.read())
        self.thumbnail.save(
            '%s_thumbnail%s' % (os.path.splitext(suf.name)[0], thumb_extension),
            suf, save=False
        )
        self.photo = self.thumbnail

    def save(self, *args, **kwargs):
        #Make thumbnail only if photo field was changed
        if self.photo != self.__original_photo:
            self.create_thumbnail()
        super(ContactPhoto, self).save()









