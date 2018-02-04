import codecs
import csv
import os
import zipfile, tarfile
import collections
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .admin import ContactResource, ContactPhotoResource
from .forms import ContactForm, ContactPhotoForm, UserSignUpForm, TemplateFormatForm, ImportFileFolderForm
from .models import Contact, ContactPhoto, Dublicate
from contact.settings import MEDIA_ROOT, DEFAULT_FORMATS_FOR_EXPORT, DEFAULT_FORMATS_FOR_IMPORT, ARCHIVE_FORMAT_FOR_IMPORT
from import_export.forms import ExportForm, ImportForm
from import_export.admin import ExportMixin
from datetime import datetime
import csv
from io import TextIOWrapper
import shutil
from tablib import Dataset

# Create your views here.

def find_dublicates(request, create=False):
    if create:
        Dublicate.objects.all().delete()
    total_count = 0
    user = request.user
    query_set = Contact.objects.filter(owner=user).order_by('mobile')
    qs_length = query_set.count()
    index = 0
    while index < qs_length:
        # print(query_set)
        mobile = query_set[index].mobile
        objects = query_set.filter(mobile=mobile)
        count = objects.count()
        if count > 1:
            total_count += count
            if create:
                dublicates = [Dublicate(contact_id=item, count=count) for item in objects]
                Dublicate.objects.bulk_create(dublicates)
        index += count
    return total_count

def extract_archive(input_archive, archive_format, base_dir):
    """
    Extract uploaded archive file to base_dir directory. Supported archive types pointed in settings
    :param input_archive: file object
    :param archive_format:
    :param user_id:
    :return:
    """
    if archive_format == 'zip':
        import zipfile
        input_file = zipfile.ZipFile(input_archive)
        for name in input_file.namelist()[1:]:
            file_path = os.path.join(base_dir, os.path.basename(name))
            file_obj = input_file.read(name)
            default_storage.save(file_path, ContentFile(file_obj))
    elif archive_format.startswith('tar'):
        import tarfile
        if archive_format == 'tar':
            mode = 'r'
        else:
            mode = 'r:' + archive_format.split('.')[1]
        input_file = tarfile.open(fileobj=input_archive, mode=mode)
        for name in input_file.getmembers()[1:]:
            file_path = os.path.join(base_dir, os.path.basename(name.name))
            file_obj = input_file.extractfile(name)
            default_storage.save(file_path, ContentFile(file_obj.read()))



def check_owner(view_func, redirect_url_name='login'):
    """
    Decorator, which check if logged in user is owner of the requested object. If False, request is redirected to login
    page with next = request url
    """

    def wrapper(*args, **kwargs):
        request = args[0]
        user = request.user
        contact = get_object_or_404(Contact, pk=kwargs['pk'])
        if user == contact.owner:
            return view_func(*args, **kwargs)
        else:
            return redirect('%s?next=%s' % (reverse(redirect_url_name), request.path))
    return wrapper


def sign_up(request):
    """
    User registration view. Create new User object, Profile object as well through post save signal.
    After creation User is authenticated and logged in with redirecting to contact list page
    :param request: http request 
    :return: new user object, profile object and redirect to main page with new user
    """
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # refresh related object in DB
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
    user = request.user
    user_contacts = Contact.objects.filter(owner=user).order_by('-star', 'firstname')
    user_contacts_last_thumb = [(contact, contact.contactphoto_set.first()) for contact in user_contacts]
    contact_count = user_contacts.count()
    dublicate_count = find_dublicates(request)
    return render(request, 'contacts/main.html', {'user_contacts': user_contacts_last_thumb, 'count': contact_count,
                                                  'dublicate_count': dublicate_count, 'user': user})


@login_required(login_url='/login/')
def dublicate_list(request):
    user = request.user
    contact_count = Contact.objects.filter(owner=user).count()
    dublicate_count = find_dublicates(request, True)
    dublicates = Dublicate.objects.filter(contact_id__owner=user).order_by('contact_id__mobile')
    return render(request, 'contacts/dublicate.html', {'dublicates': dublicates, 'count': contact_count,
                                                       'dublicate_count': dublicate_count, 'user': user})

@login_required()
def merge_dublicates(request):
    ids_from_form = request.POST.getlist('contact_id')
    mobiles = [item.mobile for item in Contact.objects.filter(id__in=ids_from_form)]
    # print('------', mobiles, '-----')
    for_delete = Contact.objects.filter(mobile__in=mobiles).exclude(id__in=ids_from_form)
    for item in for_delete:
        item.delete()
    Dublicate.objects.filter(contact_id__in=ids_from_form).delete()
    user = request.user
    contact_count = Contact.objects.filter(owner=user).count()
    dublicate_count = find_dublicates(request, True)
    dublicates = Dublicate.objects.filter(contact_id__owner=user).order_by('contact_id__mobile')
    return render(request, 'contacts/dublicate.html', {'dublicates': dublicates, 'count': contact_count,
                                                       'dublicate_count': dublicate_count, 'user': user})


@check_owner
# @login_required(login_url='/login/')
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
    if request.method == "POST":
        contact_form = ContactForm(request.POST, instance=contact_obj)
        part1 = list(contact_form)[0:4]
        part2 = list(contact_form)[4:]
        contact_photo_form = ContactPhotoForm(request.POST, request.FILES, instance=contact_photo)
        check = request.POST.get('photo-clear', False)
        # If clear check button has been checked, corresponded files are deleted
        if check:
            contact_photo.photo.delete()
            contact_photo.thumbnail.delete()
        if contact_form.is_valid() and contact_photo_form.is_valid():
            fname = contact_photo_form.cleaned_data.get('photo', False)
            # If there is uploaded file, update current row to 'active=False' and then create bound form with new instance
            contact_form.save()
            contact_photo_form.save()
            return redirect('contact_list')
    else:
        contact_form = ContactForm(instance=contact_obj)
        part1 = list(contact_form)[0:4]
        part2 = list(contact_form)[4:]
        contact_photo_form = ContactPhotoForm(instance=contact_photo)
    return render(request, 'contacts/contact_form.html',
                  {'form': contact_form, 'part1': part1, 'part2': part2, 'photo_form': contact_photo_form})


@login_required(login_url='/login/')
def new_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        part1 = list(form)[0:4]
        part2 = list(form)[4:]
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
        part1 = list(form)[0:4]
        part2 = list(form)[4:]
        contact_photo_form = ContactPhotoForm()
    return render(request, 'contacts/contact_form.html',
                  {'part1': part1, 'part2': part2, 'photo_form': contact_photo_form})


@check_owner
# @login_required(login_url='/login/')
def remove_contact(request, pk):
    contact_obj = get_object_or_404(Contact, pk=pk)
    # contact_photos = contact_obj.contactphoto_set.all()
    # for photo in contact_photos:
    #     if photo.photo:
    #         photo.photo.delete()
    #         photo.thumbnail.delete()
    contact_obj.delete()
    return redirect('contact_list')

@login_required
def bulk_delete(request):
    print(request.method)
    if request.method == 'POST':
        contact_ids = request.POST.getlist('contact_id')
        print(contact_ids)
        query = Contact.objects.filter(id__in=contact_ids)
        for item in query:
            item.delete()
    return redirect('contact_list')



# view for export contacts
@login_required(login_url='/login/')
def export_contacts(request):
    formats = DEFAULT_FORMATS_FOR_EXPORT
    if request.method == 'POST':
        form = ExportForm(formats, request.POST)
        if form.is_valid():
            file_format = formats[int(form.cleaned_data['file_format'])]()
            file_extension = file_format.get_extension()
            content_type = file_format.CONTENT_TYPE
            queryset = Contact.objects.filter(owner=request.user)
            contact_list = ContactResource().export(queryset)
            export_data = file_format.export_data(contact_list)
            _time = datetime.now().strftime('%Y-%m-%d')
            _model = ContactResource.Meta.model.__name__
            filename = '%s-%s.%s' % (_model, _time, file_extension)
            response = HttpResponse(export_data, content_type=content_type)
            # response.write(codecs.BOM_UTF8)
            response['Content-Disposition'] = 'attachment; filename = %s' % filename
            return response
    else:
        form = ExportForm(formats)
    return render(request, 'contacts/export_form.html', {'form': form})


@login_required(login_url='/login/')
def import_contacts(request):
    formats = DEFAULT_FORMATS_FOR_IMPORT
    archive_formats = ARCHIVE_FORMAT_FOR_IMPORT
    if request.method == 'POST':
        if 'import' in request.POST:
            form = ImportFileFolderForm(formats, archive_formats, request.POST, request.FILES)
            template_form = TemplateFormatForm(formats)
            if form.is_valid():
                base_dir = '{}/tmp'.format(request.user.id)
                contact_resource = ContactResource()
                file_format = formats[int(form.cleaned_data['input_format'])]()
                if file_format.CONTENT_TYPE == 'text/csv':
                    filename = TextIOWrapper(request.FILES['import_file'].file, encoding='utf-8')
                    imported_data = file_format.create_dataset(filename.read())
                else:
                    filename = request.FILES['import_file']
                    imported_data = file_format.create_dataset(filename.read())
                row_count = len(imported_data)
                imported_data.append_col([request.user.id] * row_count, header='owner')
                if request.FILES.get('photo_file', False):
                    archive_file = request.FILES['photo_file']
                    choice_num = form.cleaned_data.get('archive_format')
                    archive_format = archive_formats[int(choice_num)][0]
                    extract_archive(archive_file, archive_format, base_dir)
                # result = contact_resource.import_data(imported_data, dry_run=True,
                #                                       raise_errors=False)
                result = contact_resource.import_data(imported_data, dry_run=False, collect_failed_rows=True,
                                                      use_transactions=False)
                total_qty = imported_data.height
                del_inform = {}
                if result.has_errors():
                    import_nums = list(range(imported_data.height))
                    for (num, errors) in result.row_errors():
                        del_inform[num] = [error.error for error in errors]
                        import_nums.remove(num - 1)
                    imported_data = imported_data.subset(import_nums)
                # contact_resource.import_data(imported_data, dry_run=False)
                list_dir = default_storage.listdir(base_dir)
                for file in list_dir[1]:
                    default_storage.delete(os.path.join(base_dir, file))
                success_qty = imported_data.height
                error_qty = len(del_inform)
                return render(request, 'contacts/import_form.html', {'errors': del_inform,
                              'statistics': (total_qty, success_qty, error_qty)})
        elif 'download' in request.POST:
            template_form = TemplateFormatForm(formats, request.POST)
            if template_form.is_valid():
                file_format = formats[int(template_form.cleaned_data['file_format'])]()
                file_extension = file_format.get_extension()
                content_type = file_format.CONTENT_TYPE
                filename = 'Contact_template.{0}'.format(file_extension)
                filepath = os.path.join('import_templates', filename)
                with default_storage.open(filepath) as ftemplate:
                    response = HttpResponse(ftemplate, content_type=content_type)
                    response['Content-Disposition'] = 'attachment; filename = %s' % filename
                    return response
    else:
        form = ImportFileFolderForm(formats, archive_formats)
        template_form = TemplateFormatForm(formats)
    return render(request, 'contacts/import_form.html', {'form': form, 'template_form': template_form})

# def get_photos(request):
#     # Files (local path) to put in the .zip
#     photo_list = ContactPhotoResource().export()
#     line = str(photo_list.csv)
#     line = "\n".join(line.splitlines()[1:])
#
#     # relative to MEDIA_ROOT filepathes
#     filenames_rel = [row for row in line.split('\n') if row]
#     # list of absolute pathes
#     filenames = [os.path.join(MEDIA_ROOT, fpath) for fpath in filenames_rel]
#     zip_subdir = "photo"
#     zip_filename = "%s.zip" % zip_subdir
#
#     # Open ByteIO to grab in-memory ZIP contents
#     b = BytesIO()
#
#     # The zip compressor
#     zf = zipfile.ZipFile(b, "w")
#
#     for fpath in filenames:
#         # Calculate path for file in zip
#         fdir, fname = os.path.split(fpath)
#         zip_path = os.path.join(zip_subdir, fname)
#
#         # Add file, at correct path
#         zf.write(fpath, zip_path)
#
#     # Must close zip for all contents to be written
#     zf.close()
#
#     # Grab ZIP file from in-memory, make response with correct MIME-type
#     resp = HttpResponse(b.getvalue(), content_type="application/x-zip-compressed")
#     # ..and correct content-disposition
#     resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
#     resp['Content-length'] = b.tell()
#     return resp
