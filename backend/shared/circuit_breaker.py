import redis
from django.conf import settings
import time
from shared.exceptions import ExternalServiceUnavailable

class CircuitBreaker:
  
  def __init__(self, name, failure_threshold=3, cooldown_seconds=300):
    self.name = name
    self.failure_threshold = failure_threshold
    self.cooldown_seconds = cooldown_seconds
    broker_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0')
    if broker_url.startswith('memory://'):
      broker_url = 'redis://localhost:6379/0'
    self._redis = redis.Redis.from_url(broker_url)
    self._failures_key = f'breaker:{name}:failures'
    self._opened_at_key = f'breaker:{name}:opened_at'

  def is_open(self):
    opened_at = self._redis.get(self._opened_at_key)
    if not opened_at:
      return False
    if time.time() - float(opened_at) > self.cooldown_seconds:
      self._redis.delete(self._opened_at_key)
      self._redis.delete(self._failures_key)
      return False
    return True

  def record_success(self):
    self._redis.delete(self._failures_key)
    self._redis.delete(self._opened_at_key)

  def record_failure(self):
    failures = self._redis.incr(self._failures_key)
    self._redis.expire(self._failures_key, self.cooldown_seconds)
    if failures >= self.failure_threshold:
      self._redis.set(self._opened_at_key, time.time())

  def call(self, func, *args, **kwargs):
    if self.is_open():
      raise ExternalServiceUnavailable(service_name=self.name)
    try:
      result = func(*args, **kwargs)
      self.record_success()
      return result
    except ExternalServiceUnavailable:
      self.record_failure()
      raise

credit_bureau_breaker = CircuitBreaker('credit_bureau', failure_threshold=3, cooldown_seconds=300)