'''
Created on Aug 17, 2018

@author: qurban.ali
'''
import ldap
try:
    from . import settings
except:
    class settings(object):
        pass
    settings.DOMAIN = 'iceanimations.com'


def authenticate(username=None, password=None):
    try:
        connect = ldap.initialize('ldap://%s'%settings.DOMAIN)
        connect.set_option(ldap.OPT_REFERRALS, 0)
        connect.simple_bind_s('%s@%s'%(username, settings.DOMAIN), password)
        return connect.search_s('dc=iceanimations, dc=com', ldap.SCOPE_SUBTREE, '(&(objectClass=user) (sAMAccountName=%s))'%username)
    except Exception:
        pass
    finally:
        connect.unbind()