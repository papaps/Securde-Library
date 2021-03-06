from django.template import loader
from django.template.response import TemplateResponse
from django.views.generic import View
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from catalog.models import *
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import user_passes_test
from .forms import *
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
# Create your views here.

@user_passes_test(lambda u: u.groups.filter(name='Managers').exists(), login_url=reverse_lazy('login'))
def index(request):
    template = loader.get_template('manager/books.html')
    books = Book.objects.all()
    count_dictionary = dict()
    for b in books:
        count = BookInstance.objects.filter(book=b).count()
        count_dictionary[b] = count
    context = {
        'count_dictionary': count_dictionary,
    }
    return HttpResponse(template.render(context, request))

@user_passes_test(lambda u: u.groups.filter(name='Managers').exists(), login_url=reverse_lazy('login'))
def book_instances(request):
    template = loader.get_template('manager/book_instances.html')
    instances = BookInstance.objects.all()
    context = {
        'instances': instances,
    }
    return HttpResponse(template.render(context, request))

@user_passes_test(lambda u: u.groups.filter(name='Managers').exists(), login_url=reverse_lazy('login'))
def add_book(request):
    template = loader.get_template('manager/add_book.html')
    authors = Author.objects.all()
    publishers = Publisher.objects.all()

    if request.method == 'POST':
        book_form = BookForm(data=request.POST)
        author_form = AuthorForm(data=request.POST)
        publisher_form = PublisherForm(data=request.POST)
        
        selected_author = None   
        selected_publisher = None   
        
        if book_form.is_valid():
            if request.POST.get('author_id') is not None:
                selected_author = get_object_or_404(Author, pk=request.POST.get('author_id'))
            elif author_form.has_changed() and author_form.is_valid():
                author = author_form.save(commit=False)
                first_name = author_form.cleaned_data['first_name']
                last_name = author_form.cleaned_data['last_name']
                author.first_name = first_name
                author.last_name = last_name
                author.save()
                selected_author = Author.objects.get(id=author.id)

           
            if request.POST.get('publisher_id') is not None:
                selected_publisher = get_object_or_404(Publisher, pk=request.POST.get('publisher_id'))
            elif publisher_form.has_changed() and publisher_form.is_valid() :
                publisher_object = publisher_form.save(commit=False)
                publisher_name = publisher_form.cleaned_data['name']
                publisher_object.name = publisher_name
                publisher_object.save()
                selected_publisher = Publisher.objects.get(id=publisher_object.id)
            
            if book_form.is_valid() and selected_publisher is not None and selected_author is not None:
                book = book_form.save(commit=False)
                

                title = book_form.cleaned_data['title']
                year = book_form.cleaned_data['year']
                isbn = book_form.cleaned_data['isbn']
                
                book.title = title
                book.author = selected_author
                book.publisher = selected_publisher
                book.year = year
                book.isbn = isbn
                book.save()

                current_book = Book.objects.get(id=book.id)
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(Book).pk,
                    object_id=current_book.id,
                    object_repr=current_book.title,
                    action_flag=ADDITION)
                return redirect('manager_index')

    else:
        book_form = BookForm()
        author_form = AuthorForm()
        publisher_form = PublisherForm()

    context = {
        'authors': authors,
        'publishers': publishers,
        'book_form': book_form,
        'publisher_form': publisher_form,
        'author_form': author_form,
    }

    return HttpResponse(template.render(context, request))

@user_passes_test(lambda u: u.groups.filter(name='Managers').exists(), login_url=reverse_lazy('login'))
def add_book_instance(request):
    template = loader.get_template('manager/add_book_instance.html')
    books = Book.objects.all()
    
    if request.method == 'POST':
        book_instance_form = BookInstanceForm(request.POST)
        selected_book = None

        if book_instance_form.is_valid():
            if request.POST.get('book_id') is not None:
                selected_book = get_object_or_404(Book, pk=request.POST.get('book_id'))  
                book_instance = book_instance_form.save(commit=False)
                status = book_instance_form.cleaned_data['status']
                book_instance.status = status
                book_instance.book = selected_book
                book_instance.save()
                current_book_instance = BookInstance.objects.get(id=book_instance.id)
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(BookInstance).pk,
                    object_id=current_book_instance.id,
                    object_repr=selected_book.title,
                    action_flag=CHANGE,
                    change_message="Added Instance "+ str(current_book_instance.id))
                return redirect('book_instances')
            else:
                book_instance_form.add_error('status', 'Select a book')

    else:
        book_instance_form = BookInstanceForm()

    context = {
        'books': books,
        'book_instance_form': book_instance_form,
    }
    return HttpResponse(template.render(context, request))

@user_passes_test(lambda u: not u.is_authenticated or u.groups.filter(name='Managers').exists(), login_url=reverse_lazy('login'))
def view_book_details(request, book_id):
    template = loader.get_template('manager/book_details.html')
    selected_book = Book.objects.get(pk=book_id)
    authors = Author.objects.all()
    publishers = Publisher.objects.all()

    if request.method == 'POST':
        book_form = BookForm(data=request.POST, instance=selected_book)

        selected_author = None   
        selected_publisher = None   
        
        if book_form.is_valid():
            if request.POST.get('author_id') is not None:
                selected_author = get_object_or_404(Author, pk=request.POST.get('author_id'))
           
            if request.POST.get('publisher_id') is not None:
                selected_publisher = get_object_or_404(Publisher, pk=request.POST.get('publisher_id'))
        

            if book_form.is_valid():
                book = book_form.save(commit=False)
                book.author = selected_author
                book.publisher = selected_publisher
                book.save()
                current_book = Book.objects.get(id=book.id)
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(Book).pk,
                    object_id=current_book.id,
                    object_repr=current_book.title,
                    action_flag=CHANGE,
                    change_message="Edited Book Details")
                return redirect('manager_index')

    else:
        book_form = BookForm(instance=selected_book)

    context = {
        'book': selected_book,
        'authors': authors,
        'publishers': publishers,
        'book_form': book_form,
    }
    return HttpResponse(template.render(context, request))

@user_passes_test(lambda u: not u.is_authenticated or u.groups.filter(name='Managers').exists(), login_url=reverse_lazy('login'))
def view_book_instance_details(request, bookinstance_id):
    template = loader.get_template('manager/book_instance_details.html')
    selected_book_instance = BookInstance.objects.get(pk=bookinstance_id)
    books = Book.objects.all()
    if request.method == 'POST':
        book_instance_form = BookInstanceForm(request.POST, instance=selected_book_instance)
        selected_book = None

        if book_instance_form.is_valid():
            if request.POST.get('book_id') is not None:
                selected_book = get_object_or_404(Book, pk=request.POST.get('book_id'))     
                book_instance = book_instance_form.save(commit=False)
                status = book_instance_form.cleaned_data['status']
                book_instance.book = selected_book
                if status == 'a':
                    book_instance.past_profiles.add(book_instance.current_profile)
                    book_instance.current_profile = None
                book_instance.save()
                current_book_instance = BookInstance.objects.get(id=book_instance.id)
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(BookInstance).pk,
                    object_id=current_book_instance.id,
                    object_repr=selected_book.title,
                    action_flag=CHANGE,
                    change_message="Edited Book Instance Details")
            return redirect('book_instances')

    else:
        book_instance_form = BookInstanceForm(instance=selected_book_instance)

    context = {
        'book_instance_form': book_instance_form,
        'instance': selected_book_instance,
        'books': books,
    }
    return HttpResponse(template.render(context, request))

@user_passes_test(lambda u: u.groups.filter(name='Managers').exists(), login_url=reverse_lazy('login'))
def change_password(request):
    template = loader.get_template('manager/change_password.html')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)

        if request.user.check_password('{}'.format(request.POST.get("current_password"))) == False:
            form.set_current_password_flag()

        if form.is_valid():
            user = request.user
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['password1']
            confirm_new_password = form.cleaned_data['password2']
            check_authentication = check_password(current_password, user.password)

            if check_authentication:
                user.set_password(new_password)   
                user.save()
                LogEntry.objects.log_action(
                    user_id=user.id,
                    content_type_id=ContentType.objects.get_for_model(User).pk,
                    object_id=user.id,
                    object_repr=user.username,
                    action_flag=CHANGE,
                    change_message="Changed password")
                login_user = authenticate(request=request, username=user.username, password=new_password)
                if user is not None:
                    if user.is_active:
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return redirect('manager_index')

    else:
        form = ResetPasswordForm()
    context = {
        'reset_password_form': form,
    }
    return HttpResponse(template.render(context, request))

def delete_book(request, book_id):
    selected_book = Book.objects.get(pk=book_id)
    book_instances = BookInstance.objects.filter(book=selected_book)
    for instance in book_instances:
        instance.delete()
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(Book).pk,
        object_id=selected_book.id,
        object_repr=selected_book.title,
        action_flag=DELETION)
    selected_book.delete()
    return redirect("manager_index")

def delete_book_instance(request, bookinstance_id):
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(BookInstance).pk,
        object_id=bookinstance_id,
        object_repr= BookInstance.objects.get(pk=bookinstance_id).book.title,
        action_flag= CHANGE,
        change_message="Deleted Instance " + bookinstance_id)
    BookInstance.objects.get(pk=bookinstance_id).delete()
    return redirect("book_instances")
        
        
