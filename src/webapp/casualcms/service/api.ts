import {
  IAccountApi,
  IPageApi,
  ISiteApi,
  ISnippetApi,
  ITemplateApi,
} from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";
import { FetchTemplateApi } from "../adapters/api/template";
import { FetchPageApi } from "../adapters/api/page";
import { FetchSiteApi } from "../adapters/api/site";
import { FetchSnippetApi } from "../adapters/api/snippet";

export interface IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;
  site: ISiteApi;
  snippet: ISnippetApi;
}

export class Api implements IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;
  site: ISiteApi;
  snippet: ISnippetApi;

  constructor() {
    this.account = new FetchAccountApi();
    this.template = new FetchTemplateApi();
    this.page = new FetchPageApi();
    this.site = new FetchSiteApi();
    this.snippet = new FetchSnippetApi();
  }
}
