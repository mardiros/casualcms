import { IAccountRepository } from "../domain/repositories";

import { Database, IndexDBAccountRepository } from "../adapters/repositories";

export interface IUnitOfWork {
  account: IAccountRepository;
}

export class UnitOfWork implements IUnitOfWork {
  account: IAccountRepository;

  constructor(db: Database) {
    this.account = new IndexDBAccountRepository(db);
  }
}
