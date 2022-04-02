import { Result } from "neverthrow";

import { Account } from "./model";

interface IAccountRepository {
  getCurrent(): Promise<Result<Account, string>>;
}

export type { IAccountRepository };
