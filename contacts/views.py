import codecs
import csv
import os
import zipfile
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .admin import ContactResource, ContactPhotoResource
from .forms import ContactForm, ContactPhotoForm, UserSignUpForm
from .models import Contact, ContactPhoto
from contact.settings import MEDIA_ROOT, DEFAULT_FORMATS
from import_export.forms import ExportForm
from import_export.admin import ExportMixin
from datetime import datetime
import tablib

# Create your views here.

def sign_up(request):
    """
    User registration view. Create new User object, Profile object as well through post save signal.
    After creation User is authenticated and loged in with redirecting to contact list page  
    :param request: http request 
    :return: new user object, profile object and redirect to main page with new user
    """
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  #refresh related object in DB
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.email = form.cleaned_data.get('email')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('contact_list')
    else:
        form = UserSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required(login_url='/login/')
def contact_list(request):
    if request.user.is_authenticated():
        user = request.user
        user_contacts = Contact.objects.filter(owner=user).order_by('-star', 'lastname')
        user_contacts_last_thumb = [(contact, contact.contactphoto_set.first()) for contact in user_contacts]
        contact_count = user_contacts.count()
    return render(request, 'contacts/main.html', {'user_contacts': user_contacts_last_thumb, 'count': contact_count,
                                                  'user': user})


@login_required(login_url='/login/')
def edit_contact(request, pk):
    """
    This view creates bounded Modelforms: Contact and ContactPhoto based on Contact pk parameter. It changes contact 
    object, create ContactPhoto ohject, if it doesn't exist, or change it, if exist
    :param request: httprequest object
    :param pk: Primary key of Contact object
    :return: redirect to contact list if POST request, to the same form if GET request
    """
    contact_obj = get_object_or_404(Contact, pk=pk)
    contact_photo, created = ContactPhoto.objects.get_or_create(contact=contact_obj)
    if created:
        contact_photo.active = True
    if request.method == "POST":
        contact_form = ContactForm(request.POST, instance=contact_obj)
        contact_photo_form = ContactPhotoForm(request.POST, request.FILES, instance=contact_photo)
        check = request.POST.get('photo-clear', False)
        # If clear check button has been checked, corresponded files are deleted
        if check:
            contact_photo.photo.delete()
            contact_photo.thumbnail.delete()
        if contact_form.is_valid() and contact_photo_form.is_valid():
            fname = contact_photo_form.cleaned_data.get('photo', False)
            # If there is uploaded file, update current row to 'active=False' and then create bound form with new instance
            if fname:
                contact_photo.active = False
            contact_form.save()
            contact_photo_form.save()
            return redirect('contact_list')
    else:
        contact_form = ContactForm(instance=contact_obj)
        contact_photo_form = ContactPhotoForm(instance=contact_photo)
    return render(request, 'contacts/contact_form.html',
                  {'form': contact_form, 'photo_form': contact_photo_form})


@login_required(login_url='/login/')
def new_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        contact_photo_form = ContactPhotoForm(request.POST, request.FILES)
        if form.is_valid() and contact_photo_form.is_valid():
            contact_obj = form.save(commit=False)
            contact_obj.owner = request.user
            contact_obj.save()
            contact_photo = contact_photo_form.save(commit=False)
            contact_photo.contact = contact_obj
            contact_photo.active = True
            contact_photo.save()
            return redirect('contact_list')
    else:
        form = ContactForm()
        contact_photo_form = ContactPhotoForm()
    return render(request, 'contacts/contact_form.html', {'form': form, 'photo_form': contact_photo_form})


def remove_contact(request, pk):
    contact_obj = get_object_or_404(Contact, pk=pk)
    contact_photos = contact_obj.contactphoto_set.all()
    for photo in contact_photos:
        if photo.photo:
            photo.photo.delete()
            photo.thumbnail.delete()
    contact_obj.delete()
    return redirect('contact_list')


# view for export contacts
def export_contacts(request):
    formats = DEFAULT_FORMATS
    if request.method == 'POST':
        form = ExportForm(formats, request.POST)
        if form.is_valid():
            file_format = formats[int(form.cleaned_data['file_format'])]()
            file_extension = file_format.get_extension()
            content_type = file_format.CONTENT_TYPE
            contact_list = ContactResource().export()
            export_data = file_format.export_data(contact_list)
            _time = datetime.now().strftime('%Y-%m-%d')
            _model = ContactResource.Meta.model.__name__
            filename = '%s-%s.%s' %(_model, _time, file_extension)
            print(filename)
            response = HttpResponse(export_data, content_type=content_type)
            response.write(codecs.BOM_UTF8)
            response['Content-Disposition'] = 'attachment; filename = %s' % filename
            return response
    else:
        form = ExportForm(formats)
    return render(request, 'contacts/export_form.html', {'form': form})


def get_photos(request):
    # Files (local path) to put in the .zip
    photo_list = ContactPhotoResource().export()
    line = str(photo_list.csv)
    line = "\n".join(line.splitlines()[1:])

    # relative to MEDIA_ROOT filepathes
    filenames_rel = [row for row in line.split('\n') if row]
    # list of absolute pathes
    filenames = [os.path.join(MEDIA_ROOT, fpath) for fpath in filenames_rel]
    zip_subdir = "photo"
    zip_filename = "%s.zip" % zip_subdir

    # Open ByteIO to grab in-memory ZIP contents
    b = BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(b, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(b.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    resp['Content-length'] = b.tell()
    return resp
