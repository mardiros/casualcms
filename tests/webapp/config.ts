import { err, ok, Result } from "neverthrow";
import { Account } from "../../src/webapp/casualcms/domain/model";
import { AppConfig } from "../../src/webapp/config";
import { IUnitOfWork } from "../../src/webapp/casualcms/service/uow";
import { IAccountRepository } from "../../src/webapp/casualcms/domain/repositories";
import { FakeApi } from "./fake_api";

class FakeAccountRepository implements IAccountRepository {
  account: Result<Account, string>;

  constructor() {
    this.account = err("No account");
  }
  async getCurrent(): Promise<Result<Account, string>> {
    return this.account;
  }
  async set(model: Account): Promise<boolean> {
    this.account = ok(model);
    return true;
  }
}

class FakeUnitOfWork implements IUnitOfWork {
  account: IAccountRepository;

  constructor() {
    this.account = new FakeAccountRepository();
  }
}

const cfg = new AppConfig(new FakeUnitOfWork(), new FakeApi());

export default cfg;
