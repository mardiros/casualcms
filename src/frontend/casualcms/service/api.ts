import { IAccountApi } from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";

export interface IApi {
  account: IAccountApi;
}

export class Api implements IApi {
  account: IAccountApi;

  constructor() {
    this.account = new FetchAccountApi();
  }
}
