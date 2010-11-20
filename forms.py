from django import forms
from mysite.selfcheck.models import System, Branch, SelfCheckMachine, SelfCheckTransaction
import datetime

class dateSelect(forms.Form):
	branches=[]
	for branch in Branch.objects.all().order_by('branch_name'):
		tuple=(str(branch.branch_name), str(branch.branch_name))
		branches.append(tuple)
	months=[('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6','June'),('7', 'July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')]
	years=[('2009', '2009'), ('2010','2010'), ('2011','2011'), ('2012','2012'), ('2013','2013'), ('2014','2014')]
	smonth=forms.ChoiceField(label='Start Month:', widget=forms.Select, choices=months)
	syear=forms.ChoiceField(label='Start Year:', widget=forms.Select, choices=years)
	emonth=forms.ChoiceField(label='End Month:', widget=forms.Select, choices=months)
	eyear=forms.ChoiceField(label='End Year:', widget=forms.Select, choices=years)
	branch=forms.ChoiceField(label='Branch:', widget=forms.Select, choices=branches, required=False)
	
	