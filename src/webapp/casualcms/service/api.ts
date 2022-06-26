import { IAccountApi, IPageApi, ITemplateApi } from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";
import { FetchTemplateApi } from "../adapters/api/template";
import { PageApi } from "../adapters/api/page";

export interface IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;
}

export class Api implements IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;

  constructor() {
    this.account = new FetchAccountApi();
    this.template = new FetchTemplateApi();
    this.page = new PageApi();
  }
}
