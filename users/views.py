from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from .forms import UserProfileForm, UserForm, NewUserForm


@login_required
@transaction.atomic
def update_profile(request):
    form_valid_message = _("Changes done successfully!")
    form_invalid_message = _("Something went wrong!")
    if request.method == "POST":
        user_profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if user_profile_form.is_valid():
            user_profile_form.save()
            messages.success(request, form_valid_message)
        else:
            messages.error(request, form_invalid_message)

        return redirect("user:profile")
    else:
        user_form = UserForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, "users/profile.html", {"userform": user_form, "userprofileform": user_profile_form})


@permission_required('add_user')
def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.is_staff = True
            user.save()
            messages.success(request, _("Registration successful."))
            return redirect("metrics:index")
        messages.error(request, _("Unsuccessful registration. Invalid information."))
    form = NewUserForm()
    return render(request=request, template_name="users/register.html", context={"register_form": form})
