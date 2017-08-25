from django.forms import BaseInlineFormSet, inlineformset_factory, Form
from django import forms
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _
from .models import Contact, ContactPhoto
from contact.settings import PHOTO_SIZE
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from io import BytesIO

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

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'
        exclude = ['owner']
        labels = {'mobile': _('Mobile phone'),
                  'home_phone': _('Home phone'),
                  'star': _('Favorite'),
                  }
        widgets = {'firstname': TextInput(attrs={'placeholder': 'First', 'class': 'field-divided'}),
                  'secondname': TextInput(attrs={'placeholder': 'Second', 'class': 'field-divided'}),
                  'lastname': TextInput(attrs={'placeholder': 'Last', 'class': 'field-divided'}),
                  'mobile': TextInput(attrs={'class': 'field-long'}),
                  'home_phone': TextInput(attrs={'class': 'field-long'}),
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

 #Custom validation of file size. Reject file > PHOTO_SIZE (in settings) during upload
    def clean_photo(self):
        img = self.cleaned_data.get('photo', False)
        if img:
            #Imagefield object can take different type, which depends on existence of the file
            try:
                img_size = img._size
            except AttributeError:
                img_size = img.file.size
            if img_size > PHOTO_SIZE:
                raise ValidationError("Image file too large ( > %s b )" % PHOTO_SIZE)
            return img
        else:
            return img