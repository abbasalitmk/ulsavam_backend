from rest_framework.throttling import SimpleRateThrottle

class OTPRequestThrottle(SimpleRateThrottle):
    scope = 'otp_request'

    def get_cache_key(self, request, view):
        identifier = request.data.get('identifier')
        if not identifier:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request) + '_' + str(identifier).strip().lower()
        }
