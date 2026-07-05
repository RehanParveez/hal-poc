import pytest
from apps.wallets.tests.factories import WalletFactory
from decimal import Decimal
from queue import Queue
import threading
from apps.wallets.services import WalletService
from django.db import connections
from apps.wallets.models import WalletTransaction

@pytest.mark.django_db(transaction=True)
class TestWalletLockingUnderConcurrency:
  def test_concurrent_credits_do_not_lose_updates(self):
    wallet = WalletFactory(balance=Decimal('0'))
    thread_count = 20
    amount = Decimal('10.00')
    errors = Queue()
    def worker():
      try:
        WalletService.credit_wallet(wallet, amount=amount, txn_type = 'profit')
      except Exception as exc:
        errors.put(exc)
      finally:
        connections.close_all()

    threads = [threading.Thread(target=worker) for _ in range(thread_count)]
    for t in threads:
      t.start()
    for t in threads:
      t.join()
    assert errors.empty(), f"worker thread(s) raised: {list(errors.queue)}"
    wallet.refresh_from_db()
    assert wallet.balance == amount * thread_count
    assert WalletTransaction.objects.filter(wallet=wallet, txn_type = 'profit').count() == thread_count

  def test_concurrent_debits_cannot_overdraw_the_wallet(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('100.00')
    wallet.save() 
    amount = Decimal('80.00')
    barrier = threading.Barrier(2)
    results = Queue()

    def worker():
      barrier.wait()
      try:
        WalletService.debit_wallet(wallet, amount=amount, txn_type='fee')
        results.put('success')
      except ValueError:
        results.put('failure')
      finally:
        connections.close_all()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
      t.start()
    for t in threads:
      t.join()
    outcomes = list(results.queue)
    assert outcomes.count('success') == 1, f"expected exactly one debit to succeed, got: {outcomes}"
    assert outcomes.count('failure') == 1, f"expected exactly one debit to be rejected, got: {outcomes}"
    wallet.refresh_from_db()
    assert wallet.balance == Decimal('20.00')
    assert wallet.balance >= 0