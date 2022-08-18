import {
  IAccountApi,
  IPageApi,
  ISiteApi,
  ISnippetApi,
  IPageTypeApi,
} from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";
import { FetchPageTypeApi } from "../adapters/api/template";
import { FetchPageApi } from "../adapters/api/page";
import { FetchSiteApi } from "../adapters/api/site";
import { FetchSnippetApi } from "../adapters/api/snippet";

export interface IApi {
  account: IAccountApi;
  page_type: IPageTypeApi;
  page: IPageApi;
  site: ISiteApi;
  snippet: ISnippetApi;
}

export class Api implements IApi {
  account: IAccountApi;
  page_type: IPageTypeApi;
  page: IPageApi;
  site: ISiteApi;
  snippet: ISnippetApi;

  constructor() {
    this.account = new FetchAccountApi();
    this.page_type = new FetchPageTypeApi();
    this.page = new FetchPageApi();
    this.site = new FetchSiteApi();
    this.snippet = new FetchSnippetApi();
  }
}
