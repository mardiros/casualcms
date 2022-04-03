import { err, ok, Result } from "neverthrow";
import { Account } from "../../src/frontend/casualcms/domain/model";
import {
  ApiError,
  IAccountApi,
  Credentials,
} from "../../src/frontend/casualcms/domain/ports";
import { IApi } from "../../src/frontend/casualcms/service/api";
import { AppConfig } from "../../src/frontend/config";
import { IUnitOfWork } from "../../src/frontend/casualcms/service/uow";
import { IAccountRepository } from "../../src/frontend/casualcms/domain/repositories";

class FakeAccountApi implements IAccountApi {
  async byCredentials(creds: Credentials): Promise<Result<Account, ApiError>> {
    if (creds.password == "justincase") {
      let errMap = new Map();
      errMap.set("username", "Invalid username or password");
      return err(errMap);
    }
    return ok({
      id: "123",
      token: "abc123",
      lang: "en",
      username: creds.username,
    });
  }
}

class FakeApi implements IApi {
  account: IAccountApi;

  constructor() {
    this.account = new FakeAccountApi();
  }
}

class FakeAccountRepository implements IAccountRepository {
  account: Result<Account, string>;

  constructor() {
    this.account = err("No account");
  }
  async getCurrent(): Promise<Result<Account, string>> {
    return this.account;
  }
  async add(model: Account): Promise<boolean> {
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
