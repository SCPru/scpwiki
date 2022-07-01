from django.conf import settings
from django.db import models

from .articles import Article
from .sites import SiteLimitedModel, get_current_site

import urllib.parse


class File(SiteLimitedModel):
    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

        indexes = [models.Index(fields=['article', 'name'])]
        constraints = [models.UniqueConstraint(fields=['article', 'name', 'deleted_at'], name='%(app_label)s_%(class)s_unique')]  # logic: non-deleted files should be unique

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="Статья")

    name = models.TextField(verbose_name="Название файла")
    media_name = models.TextField(verbose_name="Название файла в ФС-хранилище")

    mime_type = models.TextField(verbose_name="MIME-тип")
    size = models.PositiveBigIntegerField(verbose_name="Размер файла")

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name="Автор файла", null=True, related_name='created_files')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name="Пользователь, удаливший файл", null=True, related_name='deleted_files')
    deleted_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.name} ({self.media_name})"

    @staticmethod
    def escape_media_name(name) -> str:
        return name.replace(':', '%3A').replace('/', '%2F')

    @property
    def media_url(self) -> str:
        site = get_current_site()
        return '//%s/%s/%s' % (site.media_domain, urllib.parse.quote(self.article.full_name), urllib.parse.quote(self.name))

    @property
    def local_media_path(self) -> str:
        site = get_current_site()
        return '%s/%s/%s/%s' % (settings.MEDIA_ROOT, self.escape_media_name(site.slug), self.escape_media_name(self.article.full_name), self.escape_media_name(self.media_name))
