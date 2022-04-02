import { IAccountApi } from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";

interface IApi {
  account: IAccountApi;
}

class Api implements IApi {
  account: IAccountApi;

  constructor() {
    this.account = new FetchAccountApi();
  }
}

export { IApi, Api };
