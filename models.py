from django.db import models
from django.forms import ModelForm
import datetime, calendar, pyodbc


class System(models.Model):

	system_name=models.CharField(max_length=50)
	last_update=models.DateField(blank=True, null=True)
	web_site=models.URLField(blank=True, null=True)
	
	def __unicode__(self):
		return self.system_name
		
	def update(self):
		today=datetime.date.today()
		if today==self.last_update: return False
		else:
			for each in SelfCheckMachine.objects.filter(branch__branch_system__system_name__icontains=self.system_name):each.update()
			for each in SelfCheckTransaction.objects.filter(items__gte=3000): each.delete() 
			self.last_update=today
			self.save()
			return True
		
	def clear_all(self):
		for each in SelfCheckTransaction.objects.all(): each.delete()
		return True
	
	
class Branch(models.Model):

	branch_name=models.CharField(max_length=50)
	branch_system=models.ForeignKey(System)
	
	def __unicode__(self):
		return self.branch_name
		
class SelfCheckMachine(models.Model):

	name=models.CharField(max_length=50)
	branch=models.ForeignKey(Branch)
	IP=models.IPAddressField()
	uname=models.CharField(max_length=50, blank=True, null=True)
	pword=models.CharField(max_length=50, blank=True, null=True)
	smbpath=models.URLField(verify_exists=False, max_length=200, blank=True, null=True)
	mdbfile=models.FilePathField(max_length=200, blank=True, null=True)
	
	def __unicode__(self):
		return self.name
	
	def update(self):
		string='DRIVER={Microsoft Access Driver (*.mdb)}; Dbq=\\\\'+str(self.IP)+'\\'+str(self.name)+'\\statistics.mdb; uid='+str(self.uname)+'; pwd='+str(self.pword)
		try: cnxn=pyodbc.connect(string)
		except pyodbc.Error: return False
		cursor=cnxn.cursor()
		cursor.execute("select LogDate from statistics")
		rows=cursor.fetchall()
		for row in rows:
			year=int(row.LogDate.split('-')[2])
			month=int(row.LogDate.split('-')[1])
			day=int(row.LogDate.split('-')[0])
			if datetime.date(year, month, day)==datetime.date.today():continue
			check=SelfCheckTransaction.objects.filter(machine__name__icontains=self.name, tran_date=datetime.date(year, month, day))
			if (not check and row.LogDate):
				trans=SelfCheckTransaction()
				rowstring=str('\''+str(row.LogDate)+'\'')
				queryst=str("select ItemsCheckedOut, ItemsErrors, SessionsTotal, LogDate from statistics where LogDate="+rowstring)
				cursor2=cnxn.cursor()
				cursor2.execute(queryst)
				entry=cursor2.fetchone()
				if entry:
					trans.machine=self
					trans.users=entry.SessionsTotal
					trans.errors=entry.ItemsErrors
					trans.items=entry.ItemsCheckedOut
					trans.tran_date=datetime.date(year, month, day)
					trans.save()
		cnxn.close()
		return True
		
		def clear_machine(self):
			for each in SelfCheckTransaction.objects.filter(machine__name__icontains=self.name): each.delete()
			return True
		
	
		
class SelfCheckTransaction(models.Model):

	machine=models.ForeignKey(SelfCheckMachine)
	tran_date=models.DateField()
	items=models.IntegerField()
	errors=models.IntegerField()
	users=models.IntegerField()
	
	def __unicode__(self):
		return self.machine.name
	
		
		
#I'm creating model forms in case I want to use them later

class SelfCheckMachineForm(ModelForm):
	class Meta:
		model=SelfCheckMachine

class SelfCheckTransactionForm(ModelForm):
	class Meta:
		model=SelfCheckTransaction
		
class BranchForm(ModelForm):
	class Meta:
		model=Branch

class SystemForm(ModelForm):
	class Meta:
		model=System


