from django.contrib import admin
from mysite.selfcheck.models import System, Branch, SelfCheckMachine, SelfCheckTransaction


admin.site.register(System)
admin.site.register(Branch)
admin.site.register(SelfCheckMachine)
admin.site.register(SelfCheckTransaction)