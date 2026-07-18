from django.test import TestCase
from shared.circuit_breaker import CircuitBreaker
from shared.exceptions import ExternalServiceUnavailable
 
class CircuitBreakerTests(TestCase):
  def _fresh_breaker(self, name_suffix):
    breaker = CircuitBreaker(f'test_breaker_{name_suffix}', failure_threshold=3, cooldown_seconds=2)
    breaker._redis.delete(breaker._failures_key, breaker._opened_at_key)
    return breaker
 
  def test_breaker_closed_by_default(self):
    self.assertFalse(self._fresh_breaker('closed_default').is_open())
 
  def test_breaker_opens_after_threshold_failures(self):
    breaker = self._fresh_breaker('opens_after_threshold')
    breaker.record_failure()
    breaker.record_failure()
    self.assertFalse(breaker.is_open())
    breaker.record_failure()
    self.assertTrue(breaker.is_open())
 
  def test_breaker_call_short_circuits_without_invoking_the_function(self):
    breaker = self._fresh_breaker('short_circuits')
    for _ in range(3):
      breaker.record_failure()
    self.assertTrue(breaker.is_open())
    calls = []
    def fake_api_call():
      calls.append(1)
      raise ExternalServiceUnavailable('test')
    with self.assertRaises(ExternalServiceUnavailable):
      breaker.call(fake_api_call)
    self.assertEqual(len(calls), 0, "the underlying function must not be called while the breaker is open")
 
  def test_success_resets_failure_count(self):
    breaker = self._fresh_breaker('resets_on_success')
    breaker.record_failure()
    breaker.record_failure()
    breaker.record_success()
    breaker.record_failure()
    self.assertFalse(breaker.is_open(), "a single failure after a reset should not immediately re-open the breaker")