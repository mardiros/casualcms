import { Result } from "neverthrow";

import { Account } from "./model";

interface IAccountRepository {
  getCurrent(): Promise<Result<Account, string>>;
  set(account: Account): Promise<boolean>;
  removeCurrent(): Promise<boolean>;
}

export type { IAccountRepository };
