from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import (
    Filmwork,
    Genre,
    Person,
)


class FilmworkGenreInline(admin.TabularInline):
    model = Genre.filmwork_set.through
    autocomplete_fields = ('genre',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('genre')


class FilmworkPersonInline(admin.TabularInline):
    model = Person.filmwork_set.through
    autocomplete_fields = ('person',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('person')


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    # отображение полей в списке
    # list_display = ('title', 'type', 'creation_date', 'rating')
    # list_filter = ('type',)
    # search_fields = ('title', 'description', 'id')

    # fields = (
    #     'title', 'type', 'description', 'creation_date', 'certificate',
    #     'file_path', 'rating',
    # )

    # inlines = [
    #     FilmworkGenreInline,
    #     FilmworkPersonInline,
    # ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            'genres',
            'persons',
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field_name_to_model = {
            'persons': Person,
            'genres': Genre,
        }

        if db_field.name in field_name_to_model:
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
            if 'queryset' not in kwargs:
                queryset = field_name_to_model[db_field.name].objects.all()
                if queryset is not None:
                    kwargs['queryset'] = queryset
            form_field = db_field.formfield(**kwargs)
            msg = 'Hold down “Control”, or “Command” on a Mac, to select more than one.'
            help_text = form_field.help_text
            form_field.help_text = '{} {}'.format(help_text, msg) if help_text else msg
            return form_field
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description', 'id')
    fields = ('name', 'description')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date')
    search_fields = ('full_name', 'birth_date')
    fields = ('full_name', 'birth_date')