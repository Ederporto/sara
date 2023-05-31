from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from users.models import UserProfile, TeamArea, Position


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class AccountUserAdmin(AuthUserAdmin):
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(AccountUserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super(AccountUserAdmin, self).change_view(*args, **kwargs)


admin.site.unregister(User)
admin.site.register(User, AccountUserAdmin)
admin.site.register(TeamArea)
admin.site.register(Position)