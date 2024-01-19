from django import template
from django.contrib.auth.models import Group
from Apps.nomina_app.models import Business, Employee

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
  group = Group.objects.get(name=group_name)
  return True if group in user.groups.all() else False

@register.simple_tag
def percent(n, total):
    try:
      return "%s" % str((float(n)/float(total))*100)
    except:
      return '0'


@register.simple_tag
def get_account_name(taxpayer_id, user):
    business = None
    business_name = ''
    if not user.is_anonymous:
      role = user.profile.role
      if role in ('S', 'A', 'B'):
        business = Business.objects.filter(user=user, taxpayer_id=taxpayer_id).only('name').first()
      elif role in ('E'):
        business = Employee.objects.filter(user=user, taxpayer_id=taxpayer_id).only('name').first()
      if business is not None:
        business_name = '' if business.name is None else business.name
    return business_name


@register.simple_tag
def get_account_name(taxpayer_id, user):
    business_id = ''
    business = None
    if not user.is_anonymous:
      role = user.profile.role
      if role in ('S', 'A', 'B'):
        business = Business.objects.filter(user=user, taxpayer_id=taxpayer_id).first()
      elif role in ('E'):
        business = Employee.objects.filter(user=user, taxpayer_id=taxpayer_id).first()
      if business is not None:
        business_id = business.encrypt
    return business_id
