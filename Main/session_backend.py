'''
My own backend for session storage
'''

from django.contrib.sessions.backends.db import SessionStore as DbSessionStore

class SessionStore(DbSessionStore):
    '''
    session storage
    '''

    def cycle_key(self):
        '''
        save keys
        '''

        super(SessionStore, self).cycle_key()
        self.save()
