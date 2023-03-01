from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType

# Create your views here.
from .forms import BlogPostModelForm
from .models import BlogPost

# CRUD

# GET -> Retrieve / List

# POST -> Create / Update / DELETE

# Create Retrieve Update Delete
author_group, created = Group.objects.get_or_create(name="Author")
editor_group, created = Group.objects.get_or_create(name="Editor")
publisher_group, created = Group.objects.get_or_create(name="Publisher")

content_type = ContentType.objects.get_for_model(BlogPost)
post_permission = Permission.objects.filter(content_type=content_type)
print([perm.codename for perm in post_permission])
# => ['add_post', 'change_post', 'delete_post', 'view_post']

for perm in post_permission:
    if perm.codename == "delete_post":
        publisher_group.permissions.add(perm)

    elif perm.codename == "change_post":
        editor_group.permissions.add(perm)
        publisher_group.permissions.add(perm)
    else:
        author_group.permissions.add(perm)
        editor_group.permissions.add(perm)
        publisher_group.permissions.add(perm)

# user = User.objects.get(username="")
# user.groups.add(author_group)  # Add the user to the Author group

#user = get_object_or_404(User, pk=user.id)


def blog_post_list_view(request):
    # list out objects 
    # could be search
    qs = BlogPost.objects.all().published() # queryset -> list of python object
    if request.user.is_authenticated:
        my_qs = BlogPost.objects.filter(user=request.user)
        qs = (qs | my_qs).distinct()
    template_name = 'blog/list.html'
    context = {'object_list': qs}
    return render(request, template_name, context) 


@staff_member_required
def blog_post_create_view(request):
    # create objects
    # ? use a form
    # request.user -> return something
    form = BlogPostModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        form = BlogPostModelForm()
    template_name = 'form.html'
    context = {'form': form}
    return render(request, template_name, context)  


def blog_post_detail_view(request, slug):
    # 1 object -> detail view
    obj = get_object_or_404(BlogPost, slug=slug)
    template_name = 'blog/detail.html'
    context = {"object": obj}
    return render(request, template_name, context)   

@staff_member_required
def blog_post_update_view(request, slug):
    obj = get_object_or_404(BlogPost, slug=slug)
    form = BlogPostModelForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
    template_name = 'form.html'
    context = {"title": f"Update {obj.title}", "form": form}
    return render(request, template_name, context)  


@staff_member_required
def blog_post_delete_view(request, slug):
    obj = get_object_or_404(BlogPost, slug=slug)
    template_name = 'blog/delete.html'
    if request.method == "POST":
        obj.delete()
        return redirect("/blog")
    context = {"object": obj}
    return render(request, template_name, context)  








