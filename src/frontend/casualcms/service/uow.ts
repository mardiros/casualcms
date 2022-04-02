import { IAccountRepository } from "../domain/repositories";

import { Database, IndexDBAccountRepository } from "../adapters/repositories";

interface IUnitOfWork {
  account: IAccountRepository;
}

class UnitOfWork implements IUnitOfWork {
  account: IAccountRepository;

  constructor(db: Database) {
    this.account = new IndexDBAccountRepository(db);
  }
}

export type { IUnitOfWork };
export { UnitOfWork };
