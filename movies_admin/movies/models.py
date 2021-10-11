import uuid

from django.core.validators import MinValueValidator, MinLengthValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeAndIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RoleType(models.TextChoices):
    ACTOR = 'actor', _('актер')
    DIRECTOR = 'director', _('директор')
    WRITER = 'writer', _('сценарист')


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('ТВ шоу')


class Genre(TimeAndIDMixin, models.Model):
    name = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True, null=True)

    class Meta:
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')
        db_table = '"content"."genre"'
        managed = False

    def __str__(self):
        return self.name


class FilmworkGenre(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    filmwork = models.ForeignKey('Filmwork', on_delete=models.CASCADE, to_field='id', db_column='film_work_id')
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, to_field='id', db_column='genre_id')
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['filmwork_id', 'genre_id'], name='film_work_genre'),
        ]
        verbose_name = _('Жанр фильма')
        verbose_name_plural = _('Жанры фильмов')
        db_table = '"content"."genre_film_work"'
        managed = False

    def __str__(self):
        return str(f'{self.filmwork} - {self.genre}')


class Person(TimeAndIDMixin, models.Model):
    full_name = models.CharField(_('ФИО'), validators=[MinLengthValidator(3)], max_length=200)
    birth_date = models.DateField(_('День рождения'), null=True, blank=True)

    class Meta:
        verbose_name = _('Персона')
        verbose_name_plural = _('Персоны')
        db_table = '"content"."person"'
        managed = False

    def __str__(self):
        return self.full_name


class PersonRole(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    filmwork = models.ForeignKey(
        'Filmwork', on_delete=models.CASCADE, to_field='id', db_column='film_work_id'
    )
    person = models.ForeignKey(
        'Person', on_delete=models.CASCADE, to_field='id', db_column='person_id'
    )
    role = models.CharField(
        _('role'),
        max_length=30,
        choices=RoleType.choices
    )
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Персона её роль')
        verbose_name_plural = _('Персоны и их роли')
        db_table = '"content"."person_film_work"'
        indexes = [
            models.Index(fields=['filmwork_id', 'person_id', 'role'], name='film_work_person_role'),
        ]
        managed = False

    def __str__(self):
        return str(f'{self.filmwork} - {self.person}')


class Filmwork(TimeAndIDMixin, models.Model):
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), null=True, blank=True)
    creation_date = models.DateField(_('Дата выхода'), null=True, blank=True)
    certificate = models.TextField(_('certificate'), null=True, blank=True)
    file_path = models.FileField(_('Путь к файлу'), upload_to='film_works/', blank=True)
    rating = models.FloatField(
        _('Рейтинг'),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=0.0
    )
    type = models.CharField(_('Тип произведения'), max_length=20, choices=FilmworkType.choices)
    genres = models.ManyToManyField(Genre, through='FilmworkGenre')

    class Meta:
        verbose_name = _('Фильм')
        verbose_name_plural = _('Фильмы')
        db_table = '"content"."film_work"'
        managed = False

    def __str__(self):
        return self.title
