import { IAccountApi, IPageApi, ISiteApi, ITemplateApi } from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";
import { FetchTemplateApi } from "../adapters/api/template";
import { PageApi } from "../adapters/api/page";
import { SiteApi } from "../adapters/api/site";

export interface IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;
  site: ISiteApi;
}

export class Api implements IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;
  site: ISiteApi;

  constructor() {
    this.account = new FetchAccountApi();
    this.template = new FetchTemplateApi();
    this.page = new PageApi();
    this.site = new SiteApi();
  }
}
