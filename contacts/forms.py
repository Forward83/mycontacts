from django.forms import BaseInlineFormSet, inlineformset_factory, Form
from django import forms
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _
from .models import Contact, ContactPhoto
from contact.settings import PHOTO_SIZE
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from import_export.forms import ExportForm, ImportForm
from contact.settings import MAX_SIZE_PHOTO_ARCHIVE

def photo_file_size(value): # validator for archive photo field
    limit = MAX_SIZE_PHOTO_ARCHIVE
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed {} B.'.format(MAX_SIZE_PHOTO_ARCHIVE))

class ImportFileFolderForm(ImportForm):
    photo_file = forms.FileField(label=_('Select archive file with photos'), required=False, validators=[photo_file_size])
    archive_format = forms.ChoiceField(
        label=_('Archive format'),
        choices=(),
        required=False,
    )

    def __init__(self, import_formats, archive_formats, *args, **kwargs):
        ImportForm.__init__(self, import_formats, *args, **kwargs)
        archive_choices = []
        for i, f in enumerate(archive_formats):
            archive_choices.append((str(i), f().get_title(),))
        if len(archive_choices) > 1:
            archive_choices.insert(0, ('', '---'))
        self.fields['archive_format'].choices = archive_choices


class TemplateFormatForm(ExportForm):
    file_format = forms.ChoiceField(
        label=_('Template format'),
        choices=(),
        )

    def __init__(self, formats, *args, **kwargs):
        ExportForm.__init__(self, formats, *args, **kwargs)


class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']
        widgets = {'username': TextInput(attrs={'class': 'field-divided'}),
                   'password1': TextInput(attrs={'class': 'field-divided'}),
                   'password2': TextInput(attrs={'class': 'field-divided'}),
                   'first_name': TextInput(attrs={'class': 'field-long'}),
                   'last_name': TextInput(attrs={'class': 'field-long'}),
                   'email': TextInput(attrs={'class': 'field-long'})}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        print(email)
        print(User.objects.filter(email=email))
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('User with such email already exists')
        return email


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'
        exclude = ['owner']
        labels = {'mobile': _('Mobile phone'),
                  'personal_phone': _('Personal phone'),
                  'star': _('Favorite'),
                  }
        widgets = {'firstname': TextInput(attrs={'placeholder': 'First', 'class': 'field-divided'}),
                  'secondname': TextInput(attrs={'placeholder': 'Second', 'class': 'field-divided'}),
                  'lastname': TextInput(attrs={'placeholder': 'Last', 'class': 'field-divided'}),
                  'personal_phone': TextInput(attrs={'class': 'field-long'}),
                  'position': TextInput(attrs={'class': 'field-long field-textarea'}),
                  'address': TextInput(attrs={'class': 'field-long field-textarea'}),
                  'email': TextInput(attrs={'class': 'field-long'}),
                  }
        help_texts = {
                    'mobile': 'Format: +380(67)XXXXXXX'
            }

class ContactPhotoForm(forms.ModelForm):
    class Meta:
        model = ContactPhoto
        fields = ['photo']
        labels = {'photo': _('Profile photo')}

# Custom validation of file size. Reject file > PHOTO_SIZE (in settings) during upload
    def clean_photo(self):
        img = self.cleaned_data.get('photo', False)
        if img:
            # ImageField object can take different type, which depends on existence of the file
            try:
                img_size = img._size
            except AttributeError:
                img_size = img.file.size
            if img_size > PHOTO_SIZE:
                raise ValidationError("Image file too large ( > %s b )" % PHOTO_SIZE)
            return img
        else:
            return img