from django import template
from django.contrib.auth.models import Group
from Apps.nomina_app.models import Business, Employee, News

from django.shortcuts import get_object_or_404
from django.db.models import Q
import logging 


register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
  group = Group.objects.get(name=group_name)
  return True if group in user.groups.all() else False

@register.simple_tag
def list_business():
	business = []

	try:
		list_business = Business.objects.filter()
		for lb in list_business:
			business.append({ 'id': lb.id, 'name': lb.name })
	except Exception as e:
		print ('Exception in list_business tag => {e}')
	return business

@register.simple_tag
def news_bell(request):
	list_news = []
	news = []
	total = 0
	try:
		active_taxpayer_id = request.session.get('active_account', None)

		if request.user.role == 'B':
			if active_taxpayer_id:
				try:
					account = Business.objects.get(taxpayer_id=active_taxpayer_id, user=request.user)
					news = News.objects.filter(business=account)
				except:
					news = News.objects.none()
		elif request.user.role == 'E':
			if active_taxpayer_id:
				try:
					account = Employee.objects.get(taxpayer_id=active_taxpayer_id, user=request.user)
					news = News.objects.filter(employee=account)
				except:
					news = News.objects.none()
		else:
			news = News.objects.filter(employee=None, business=None)
		news = news.filter(read=False).order_by('-date_created')
		total = news.count()
		news = news[:3]
	except Exception as e:
		print ('Exception in news_bell => %s' % e)

	for _n in news:
		list_news.append({ 'id': _n.id, 'title': _n.title, 'description': _n.description, 'date': _n.date_created })

	return { 'total': total, 'news': list_news }


@register.simple_tag
def list_news(request):
	list_news = []
	user = request.user
	account = None
	try:
		news = News.objects.none()
		active_taxpayer_id = request.session.get('active_account', None)
		if user.role == 'B':
			#if active_taxpayer_id:
			account = Business.objects.get(user=user, taxpayer_id=active_taxpayer_id)
			news = News.objects.filter(business=account)
		elif user.role == 'E':
			account = Employee.objects.get(user=user, taxpayer_id=active_taxpayer_id)
			news = News.objects.filter(employee=account)
		else:
			news = News.objects.filter(employee=None, business=None)
		news = news.order_by('-date_created')

		for _n in news:
			list_news.append({'id': _n.id, 'title': _n.title, 'description': _n.description, 'read': _n.read })
	except Exception as e:
		print( 'Exception in list_news tag => %s' % e)

	return list_news