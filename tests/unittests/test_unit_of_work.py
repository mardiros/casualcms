from datetime import datetime

from casualcms.domain.messages import Event
from casualcms.domain.model import Account
from casualcms.service.unit_of_work import AbstractUnitOfWork


class DummyEvent(Event):
    pass


async def test_accounts_repository(uow: AbstractUnitOfWork):
    bob = Account(
        id="abc",
        created_at=datetime.now(),
        username="bob",
        password="secret",
        email="bob@alice.net",
        lang="en",
    )
    async with uow as uow:
        await uow.accounts.add(bob)
    bob_fetched = await uow.accounts.by_username("bob")
    assert bob_fetched.is_ok()
    assert bob_fetched.unwrap().id == bob.id

    alice = await uow.accounts.by_username("alice")
    assert alice.is_err()


async def test_account_message(uow: AbstractUnitOfWork):
    account = Account(
        id="abc",
        created_at=datetime.now(),
        username="",
        password="xxx",
        email="",
        lang="",
    )
    evt = DummyEvent()
    account.events.append(evt)
    async with uow as uow:
        uow.accounts.seen.add(account)
        events = list(uow.collect_new_events())
        assert events == [evt]


async def test_rollback(uow: AbstractUnitOfWork):
    try:
        async with uow:
            raise Exception("Failed")
    except Exception:
        pass
    assert uow.committed is False  # type: ignore


async def test_no_autocommit(uow: AbstractUnitOfWork):
    async with uow:
        pass
    assert uow.committed is None  # type: ignore
    await uow.commit()
    assert uow.committed is True  # type: ignore
