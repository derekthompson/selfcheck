from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.datastructures import SortedDict
from mysite.selfcheck.models import System, Branch, SelfCheckMachine, SelfCheckTransaction
from mysite.selfcheck.forms import dateSelect
from django.template import RequestContext
import datetime, calendar, pyodbc


class DataStuff():

	def graphTotals(request, smonth=1, syear=2010, emonth=12, eyear=2010):
		users=''
		errors=''
		items=''
		type=''
		if smonth==emonth and syear==eyear: type='&cht=bvg'
		else: type='&cht=lxy'
		while(not((syear==eyear) and (smonth>emonth))):
			if smonth==13:
				smonth=1
				syear+=1
			usercount=0
			errorcount=0
			itemcount=0
			for monthly_SelfCheckTransactions in SelfCheckTransaction.objects.filter(tran_date__range=(datetime.date(syear, smonth,1), datetime.date(syear, smonth, calendar.monthrange(syear, smonth)[1]))):
				usercount+=monthly_SelfCheckTransactions.users
				itemcount+=monthly_SelfCheckTransactions.items
			users=users+str(usercount)+','
			items=items+str(itemcount)+','
			smonth+=1
		users=users.rstrip(',')
		items=items.rstrip(',')
		if type=='&cht=bvg': data='&chd=t:'+users+'|'+items
		else: data='&chd=t:-1|'+users+'|-1|'+items
		url='http://chart.apis.google.com/chart?chs=390x300&chxt=y&chds=0,42000&chxr=0,0,42000,3000'+type+'&chco=FF0000,0000FF'+data+'&chdl=Users|Items&chdlp=b&chls=2,4,1|2,4,1&chma=5,5,5,25&chtt=System+Totals'
		return url
	
	
	def graphBranches(request, smonth=1, syear=2010, emonth=12, eyear=2010):
		items=''
		if smonth==emonth and syear==eyear: type='&cht=bvg'
		else: type='&cht=lxy'
		results={}
		for branch in Branch.objects.all().order_by('branch_name'):
			sy=syear
			sm=smonth
			ey=eyear
			em=emonth
			brname=str(branch.branch_name)
			branchlist=[]
			while(not((sy==ey) and (sm>em))):
				if sm==13:
					sm=1
					sy+=1
				usercount=0
				for monthly_SelfCheckTransactions in SelfCheckTransaction.objects.filter(machine__branch__branch_name__icontains=branch.branch_name, tran_date__range=(datetime.date(sy, sm,1), datetime.date(sy, sm, calendar.monthrange(sy, sm)[1]))):
					usercount+=monthly_SelfCheckTransactions.users
				branchlist.append(usercount)
				sm+=1
			results[branch]=branchlist
		chdata='&chd=t:'
		chitems='|'
		chlabels='&chdl='
		for keys, values in results.items():
			chlabels=chlabels+str(keys)+'|'
			if type!='&cht=bvg': chdata=chdata+'-1|'
			for each in values:
				chdata=chdata+str(each)+','
			chdata=chdata.rstrip(',')
			chdata=chdata+'|'
		chlabels=chlabels.rstrip('|')
		chdata=chdata.rstrip('|')
		url='http://chart.apis.google.com/chart?chs=390x300&chxt=y&chdlp=b&chxr=0,0,6000,500&chco=FF0000,00FF00,0000FF,49188F,990066,3072F3,80C65A&chds=0,6000'+type+chdata+chlabels+'&chtt=Total+Users+Served+by+Branch'
		return url

	def BranchStats(request, smonth=1, syear=2010, emonth=12, eyear=2010, branch=Branch(id=1).branch_name):
		items=''
		users=''
		branch_data=[]
		monthly_data=SortedDict()
		if smonth==emonth and syear==eyear: type='&cht=bvg'
		else: type='&cht=lxy'
		totalitems=0
		totalusers=0
		sy=syear
		sm=smonth
		ey=eyear
		em=emonth
		while(not((sy==ey) and (sm>em))):
			if sm==13:
				sm=1
				sy+=1
			usercount=0
			itemcount=0
			for monthly_SelfCheckTransactions in SelfCheckTransaction.objects.filter(machine__branch__branch_name__icontains=branch, tran_date__range=(datetime.date(sy, sm,1), datetime.date(sy, sm, calendar.monthrange(sy, sm)[1]))):
				usercount+=monthly_SelfCheckTransactions.users
				itemcount+=monthly_SelfCheckTransactions.items
			date=str(sm)+'/'+str(sy)
			users=users+str(usercount)+','
			items=items+str(itemcount)+','
			monthly_data[date]={'Users':usercount, 'Items':str(itemcount)}
			totalitems+=itemcount
			totalusers+=usercount
			sm+=1
		monthly_data['Branch Totals']={'Users':totalusers, 'Items':totalitems}
		users=users.rstrip(',')
		items=items.rstrip(',')
		if type=='&cht=bvg': data='&chd=t:'+users+'|'+items
		else: data='&chd=t:-1|'+users+'|-1|'+items
		url='http://chart.apis.google.com/chart?chs=390x300&chxt=y&chds=0,6000&chxr=0,0,6000,500'+type+'&chco=FF0000,0000FF'+data+'&chdl=Users|Items&chdlp=b&chls=2,4,1|2,4,1&chma=5,5,5,25&chtt='+branch+'+Totals'
		branch_data=[monthly_data, url]
		return branch_data
		
							
	def system_selfcheck_stats(request, smonth=1, syear=2010, emonth=12, eyear=2010):
		systotal_users=0
		systotal_items=0
		system_data=SortedDict()
		for branch in Branch.objects.all().order_by('branch_name'):
			branch_data={}
			total_users=0
			total_items=0
			if not SelfCheckMachine.objects.filter(name__icontains=branch).order_by('name'): continue
			for mach in SelfCheckMachine.objects.filter(name__icontains=branch).order_by('name'):
				#It's worth noting the next line because it's the best way to find the end of a month for the requirement with datetime.date(year, month, day)
				for mach_SelfCheckTransactions in SelfCheckTransaction.objects.filter(machine__name__icontains=mach.name, tran_date__range=(datetime.date(syear, smonth, 1), datetime.date(eyear, emonth, calendar.monthrange(eyear, emonth)[1]))):
					total_users+=mach_SelfCheckTransactions.users
					total_items+=mach_SelfCheckTransactions.items
			systotal_users+=total_users
			systotal_items+=total_items
			branch_data={u'Total Users': total_users, u'Total Items': total_items}
			system_data[branch.branch_name]=branch_data
		system_data[u'System Totals']={u'Total Users': systotal_users, u'Total Items': systotal_items}
		return system_data		
	
	
def index(request):
	errors=[]
	graph=''
	system_data={}
	current_date=str(datetime.date.today()).split('-')
	smonth=int(current_date[1])
	emonth=int(current_date[1])
	syear=int(current_date[0])
	eyear=int(current_date[0])
	if request.method == 'POST':
		form=dateSelect(request.POST)
		if form.is_valid():
			smonth=int(form.cleaned_data['smonth'])
			syear=int(form.cleaned_data['syear'])
			emonth=int(form.cleaned_data['emonth'])
			eyear=int(form.cleaned_data['eyear'])
			if syear>eyear or ((syear==eyear) and (emonth<smonth)):errors.append('Your date range is invalid!')
	else: 
		form=dateSelect(initial={'smonth':smonth, 'syear':syear, 'emonth':emonth, 'eyear':eyear})
		for each in System.objects.all():
			each.update()
	if errors: return render_to_response('selfcheck/index.html',{'form':form, 'errors':errors}, context_instance=RequestContext(request))
	data=DataStuff()
	system_data=data.system_selfcheck_stats(smonth, syear, emonth, eyear)
	graph=[]
	graph.append(data.graphTotals(smonth, syear, emonth, eyear))
	graph.append(data.graphBranches(smonth, syear, emonth, eyear))
	return render_to_response('selfcheck/index.html', {'system_data': system_data, 'form':form, 'errors':errors, 'graph':graph}, context_instance=RequestContext(request))
	
def branches(request, branch):
	errors=[]
	graph=''
	branch_data=[]
	current_date=str(datetime.date.today()).split('-')
	smonth=int(current_date[1])
	emonth=int(current_date[1])
	syear=int(current_date[0])
	eyear=int(current_date[0])
	if request.method == 'POST':
		form=dateSelect(request.POST)
		if form.is_valid():
			smonth=int(form.cleaned_data['smonth'])
			syear=int(form.cleaned_data['syear'])
			emonth=int(form.cleaned_data['emonth'])
			eyear=int(form.cleaned_data['eyear'])
			branch=str(form.cleaned_data['branch'])
			if syear>eyear or ((syear==eyear) and (emonth<smonth)):errors.append('Your date range is invalid!')
	else:form=dateSelect(initial={'smonth':smonth, 'syear':syear, 'emonth':emonth, 'eyear':eyear})
	if errors: return render_to_response('selfcheck/branches.html',{'form':form, 'errors':errors}, context_instance=RequestContext(request))
	data=DataStuff()
	branch_data=data.BranchStats(smonth, syear, emonth, eyear, branch)
	monthly_data=branch_data[0]
	graph=branch_data[1]
	return render_to_response('selfcheck/branches.html', {'branch': branch, 'monthly_data': monthly_data, 'form':form, 'errors':errors, 'graph':graph}, context_instance=RequestContext(request))
	

		