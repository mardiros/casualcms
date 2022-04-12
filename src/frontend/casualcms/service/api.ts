import { IAccountApi, ITemplateApi } from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";
import { FetchTemplateApi } from "../adapters/api/template";

export interface IApi {
  account: IAccountApi;
  template: ITemplateApi;
}

export class Api implements IApi {
  account: IAccountApi;
  template: ITemplateApi;

  constructor() {
    this.account = new FetchAccountApi();
    this.template = new FetchTemplateApi();
  }
}
