import { openDB, DBSchema, IDBPDatabase } from "idb";
import { Result, ok, err } from "neverthrow";
import { IAccountRepository } from "casualcms/domain/repositories";
import { Account } from "casualcms/domain/model";

interface AppDBSchema extends DBSchema {
  default: {
    key: "account";
    value: string;
  };
  account: {
    key: string;
    value: Account;
  };
}

export type Database = IDBPDatabase<AppDBSchema>;

export const initDB = async (): Promise<Database> => {
  const db = await openDB<AppDBSchema>("casualcms", 1, {
    upgrade(db) {
      db.createObjectStore("default");
      db.createObjectStore("account");
    },
  });
  return db as Database;
};

class IndexDBRepository {
  db: Database;
  constructor(db: Database) {
    this.db = db;
  }
}

export class IndexDBAccountRepository
  extends IndexDBRepository
  implements IAccountRepository
{
  async getCurrent(): Promise<Result<Account, string>> {
    const key = await this.db.get("default", "account");
    if (!key) {
      return err("No default account");
    }
    const accountKey = key as string;
    const account = await this.db.get("account", accountKey);
    if (!account) {
      return err("Default account does not exists");
    }
    return ok(account as Account);
  }
}
