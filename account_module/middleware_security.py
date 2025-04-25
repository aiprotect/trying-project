from django.core.cache import cache
from django.http import JsonResponse
from ipware import get_client_ip
import re
import logging
import time
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from user_agents import parse
from django.shortcuts import render
from hashlib import sha256

logger = logging.getLogger('security')

class AdvancedSecurityMiddleware:
    """
    میدل‌ور امنیتی پیشرفته با قابلیت‌های:
    - محافظت در برابر حملات مختلف
    - مدیریت محدودیت نرخ درخواست
    - افزودن هدرهای امنیتی
    - تشخیص رفتارهای مشکوک
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.threat_levels = {
            'low': {'score': 10, 'action': 'log'},
            'medium': {'score': 30, 'action': 'captcha'},
            'high': {'score': 70, 'action': 'temp_block'},
            'critical': {'score': 100, 'action': 'perm_block'}
        }
        
        self.security_config = getattr(settings, 'SECURITY_CONFIG', {
            'rate_limits': {
                'global': {'requests': 300, 'window': 60},
                'auth': {'requests': 10, 'window': 300},
                'api': {'requests': 100, 'window': 60},
            },
            'threat_patterns': [
                {'pattern': r'(<script>|<\/script>)', 'type': 'xss', 'score': 40},
                {'pattern': r'(union\s+select|drop\s+table)', 'type': 'sql_injection', 'score': 60},
                {'pattern': r'(\.\.\/|\.\/)', 'type': 'path_traversal', 'score': 50},
                {'pattern': r'(curl\s|wget\s|bash\s)', 'type': 'command_injection', 'score': 70},
            ],
            'exempt_paths': ['/static/', '/media/', '/healthz/'],
            'security_headers': {
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:",
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'SAMEORIGIN',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload'
            }
        })

    def __call__(self, request):
        # معاف کردن مسیرهای استاتیک و مدیا
        if any(request.path.startswith(exempt) for exempt in self.security_config['exempt_paths']):
            return self.get_response(request)
            
        # جمع‌آوری اطلاعات درخواست
        client_ip = get_client_ip(request)[0] or 'unknown'
        user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
        
        # بررسی درخواست‌های پیش‌پرواز CORS
        if self._is_preflight_request(request):
            return self.get_response(request)
            
        try:
            # ارزیابی امنیتی درخواست
            threat_assessment = self._assess_threat(request, client_ip, user_agent)
            
            # اقدامات امنیتی بر اساس سطح تهدید
            if threat_assessment.get('level', 'low') != 'low':
                return self._handle_threat(request, threat_assessment)
                
            # اعمال محدودیت نرخ
            if self._is_rate_limited(request, client_ip):
                return self._rate_limit_response(request)
                
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}", exc_info=True)
            
        # پردازش درخواست و پاسخ
        response = self.get_response(request)
        
        # افزودن هدرهای امنیتی
        if self._should_add_headers(response):
            self._add_security_headers(response)
            
        return response

    def _should_add_headers(self, response):
        """تعیین آیا هدرهای امنیتی باید اضافه شوند"""
        content_type = response.get('Content-Type', '')
        return (
            not response.streaming and
            not getattr(response, 'is_async', False) and
            content_type.startswith(('text/html', 'application/json'))
        )

    def _generate_request_fingerprint(self, request, ip):
        """تولید شناسه منحصر به فرد برای درخواست"""
        fingerprint_data = f"{ip}-{request.method}-{request.path}-{request.META.get('HTTP_USER_AGENT','')}"
        return sha256(fingerprint_data.encode()).hexdigest()

    def _is_preflight_request(self, request):
        """بررسی درخواست‌های پیش‌پرواز CORS"""
        return (
            request.method == 'OPTIONS' and 
            'HTTP_ORIGIN' in request.META and 
            'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META
        )

    def _assess_threat(self, request, ip, user_agent):
        """ارزیابی جامع تهدیدات امنیتی"""
        threat_score = 0
        detected_threats = []
        
        # بررسی الگوهای مخرب در داده‌های درخواست
        request_data = {
            'get': str(request.GET),
            'post': str(request.POST),
            'headers': str(request.META),
            'body': str(getattr(request, 'body', ''))
        }
        
        for pattern in self.security_config['threat_patterns']:
            if re.search(pattern['pattern'], 
                       request_data['get'] + request_data['post'] + request_data['headers'], 
                       re.IGNORECASE):
                threat_score += pattern['score']
                detected_threats.append({
                    'type': pattern['type'],
                    'pattern': pattern['pattern'],
                    'score': pattern['score']
                })
        
        # تحلیل رفتار کاربر
        behavior_score = self._analyze_behavior(request, ip, user_agent)
        threat_score += behavior_score
        
        # تعیین سطح تهدید
        threat_level = 'low'
        for level, config in sorted(self.threat_levels.items(), 
                                  key=lambda x: x[1]['score'], 
                                  reverse=True):
            if threat_score >= config['score']:
                threat_level = level
                break
                
        return {
            'score': threat_score,
            'level': threat_level,
            'threats': detected_threats,
            'behavior_score': behavior_score,
            'ip': ip,
            'user_agent': str(user_agent)
        }

    def _analyze_behavior(self, request, ip, user_agent):
        """تحلیل رفتار کاربر"""
        score = 0
        
        # بررسی سرعت درخواست‌ها
        request_rate = self._get_request_rate(ip)
        if request_rate > 10:  # بیش از 10 درخواست در ثانیه
            score += 20
        
        # بررسی فعالیت غیرعادی در صفحات حساس
        if request.path in ['/login/', '/register/']:
            if not request.META.get('HTTP_X_MOUSE_MOVEMENT', ''):
                score += 15
        
        # بررسی تغییرات ناگهانی User-Agent
        last_ua = cache.get(f'last_ua:{ip}')
        if last_ua and last_ua != str(user_agent):
            score += 25
            
        return score

    def _get_request_rate(self, ip):
        """محاسبه تعداد درخواست‌های اخیر یک IP"""
        cache_key = f"request_rate:{ip}"
        request_times = cache.get(cache_key, [])
        
        now = time.time()
        recent_requests = [t for t in request_times if now - t < 10]
        
        cache.set(cache_key, recent_requests + [now], timeout=10)
        return len(recent_requests)

    def _is_rate_limited(self, request, ip):
        """محدودیت نرخ هوشمند"""
        path = request.path
        
        # بررسی مسیرهای معاف
        if any(path.startswith(exempt) for exempt in self.security_config['exempt_paths']):
            return False
            
        # محدودیت کلی
        global_key = f"rate:global:{ip}"
        global_count = cache.get(global_key, 0)
        if global_count >= self.security_config['rate_limits']['global']['requests']:
            return True
        cache.set(global_key, global_count + 1, 
                self.security_config['rate_limits']['global']['window'])
        
        # محدودیت برای مسیرهای خاص
        if path.startswith('/api/'):
            api_key = f"rate:api:{ip}"
            api_count = cache.get(api_key, 0)
            if api_count >= self.security_config['rate_limits']['api']['requests']:
                return True
            cache.set(api_key, api_count + 1, 
                     self.security_config['rate_limits']['api']['window'])
            
        elif path in ['/login/', '/register/', '/password-reset/']:
            auth_key = f"rate:auth:{ip}"
            auth_count = cache.get(auth_key, 0)
            if auth_count >= self.security_config['rate_limits']['auth']['requests']:
                return True
            cache.set(auth_key, auth_count + 1, 
                     self.security_config['rate_limits']['auth']['window'])
            
        return False

    def _handle_threat(self, request, threat_assessment):
        """مدیریت تهدیدات شناسایی شده"""
        action = self.threat_levels[threat_assessment['level']]['action']
        
        logger.warning(
            f"Threat detected - IP: {threat_assessment['ip']}, "
            f"Score: {threat_assessment['score']}, "
            f"Threats: {[t['type'] for t in threat_assessment['threats']]}"
        )
        
        if action == 'captcha':
            return self._challenge_response(request, 'captcha')
        elif action == 'temp_block':
            cache.set(f'block:{threat_assessment["ip"]}', True, 900)
            return self._block_response(request, threat_assessment, temp=True)
        elif action == 'perm_block':
            cache.set(f'perm_block:{threat_assessment["ip"]}', True, None)
            return self._block_response(request, threat_assessment, temp=False)
            
        return self.get_response(request)

    def _challenge_response(self, request, challenge_type):
        """پاسخ با چالش امنیتی"""
        if challenge_type == 'captcha':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'challenge',
                    'challenge': 'captcha',
                    'message': 'لطفاً چالش امنیتی را کامل کنید'
                }, status=429)
                
            return render(request, 'security/challenge.html', {
                'challenge_type': 'captcha',
                'redirect_to': request.get_full_path()
            }, status=429)

    def _block_response(self, request, threat_assessment, temp=True):
        """پاسخ مسدودسازی"""
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'code': 403 if not temp else 429,
                'message': 'دسترسی شما موقتاً محدود شده است' if temp else 'دسترسی شما مسدود شده است',
                'threat_level': threat_assessment['level'],
                'block_time': '15 minutes' if temp else 'permanent',
                'contact_support': True
            }, status=403 if not temp else 429)
            
        return render(request, 'security/blocked.html', {
            'temp_block': temp,
            'threat_info': threat_assessment,
            'contact_email': getattr(settings, 'SECURITY_CONTACT_EMAIL', 'security@example.com')
        }, status=403 if not temp else 429)

    def _rate_limit_response(self, request):
        """پاسخ محدودیت نرخ"""
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'code': 429,
                'message': 'تعداد درخواست‌های شما بیش از حد مجاز است',
                'retry_after': 60
            }, status=429)
            
        return render(request, 'security/rate_limit.html', status=429)

    def _add_security_headers(self, response):
        """افزودن هدرهای امنیتی"""
        for header, value in self.security_config['security_headers'].items():
            # عدم اعمال CSP روی صفحات مدیریت
            if header == 'Content-Security-Policy' and hasattr(settings, 'ADMIN_PATH'):
                if response._request.path.startswith(settings.ADMIN_PATH):
                    continue
            response[header] = value

    def _log_request(self, request, ip, user_agent, request_time, threat_assessment):
        """ثبت اطلاعات درخواست"""
        log_data = {
            'timestamp': request_time.isoformat(),
            'ip': ip,
            'method': request.method,
            'path': request.path,
            'user_agent': str(user_agent),
            'threat_score': threat_assessment['score'],
            'threat_level': threat_assessment['level'],
            'detected_threats': threat_assessment['threats'],
            'user': str(request.user) if not isinstance(request.user, AnonymousUser) else 'anonymous'
        }
        logger.info(log_data)