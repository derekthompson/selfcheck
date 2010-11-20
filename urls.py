from django.conf.urls.defaults import *

urlpatterns = patterns('',
	('^$', 'mysite.selfcheck.views.index'),
	('^index/$', 'mysite.selfcheck.views.index'),  
	('^branches/(\w+)/$', 'mysite.selfcheck.views.branches'), 
)
