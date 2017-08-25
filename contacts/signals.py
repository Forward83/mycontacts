# from django.db.models.signals import post_init, post_save
# from django.dispatch import receiver
# from contacts.models import ContactPhoto
#
# @receiver(post_init, sender=ContactPhoto)
# def backup_files_path(sender, instance, **kwargs):
#     instance._current_photo = instance.photo
#     instance._current_thumb = instance.thumbnail
#
# @receiver(post_save, sender=ContactPhoto)
# def delete_old_files(sender, instance, **kwargs):
#     print(instance.photo.path)
#     print(instance._current_photo.path)
#     if hasattr(instance, '_current_photo'):
#         if instance.photo.path != instance._current_photo.path:
#             instance._current_photo.delete(save=True)
#             instance._current_thumb.delete(save=False)
