from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Publisher, Author, Book, BookInstance, Review, Profile

# Register your models here.
# admin.site.register(Review)

admin.site.register(Profile)

class BookInline(admin.TabularInline):
    model = Book
    fieldsets = (
        ('BOOKS', {
            'fields': ('title', 'isbn', 'author', 'publisher', 'year')
        }),
    )

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    fields = ['first_name', 'last_name']
    inlines = [BookInline]

# admin.site.register(Author, AuthorAdmin)

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'year')
    inlines = [BooksInstanceInline]

class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'id', 'current_profile',)
    list_filter = ('status',)
    filter_horizontal = ('past_profiles',)

    fieldsets = (
        (None, {
            'fields': ('book', 'id')
        }),
        ('Availability', {
            'fields': ('status',)
        }),
    )


# admin.site.register(Book, BookAdmin)
# admin.site.register(BookInstance, BookInstanceAdmin)

class LibraryManagerSite(AdminSite):
    site_header = "Library Manager"
    site_title = "Library Manager Portal"
    index_title = "Welcome to Library Manager Portal"

library_manager_site = LibraryManagerSite(name='library_manager')

library_manager_site.register(Publisher)
library_manager_site.register(Review)
library_manager_site.register(Book, BookAdmin)
library_manager_site.register(BookInstance, BookInstanceAdmin)
library_manager_site.register(Author, AuthorAdmin)