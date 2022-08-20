import {
  IAccountApi,
  IPageApi,
  ISiteApi,
  ISnippetApi,
  IPageTypeApi,
  ISnippetTypeApi,
} from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";
import { FetchPageTypeApi } from "../adapters/api/page_type";
import { FetchPageApi } from "../adapters/api/page";
import { FetchSiteApi } from "../adapters/api/site";
import { FetchSnippetApi } from "../adapters/api/snippet";
import { FetchSnippetTypeApi } from "../adapters/api/snippet_type";

export interface IApi {
  account: IAccountApi;
  pageType: IPageTypeApi;
  page: IPageApi;
  site: ISiteApi;
  snippet: ISnippetApi;
  snippetType: ISnippetTypeApi;
}

export class Api implements IApi {
  account: IAccountApi;
  page: IPageApi;
  pageType: IPageTypeApi;
  site: ISiteApi;
  snippet: ISnippetApi;
  snippetType: ISnippetTypeApi;

  constructor() {
    this.account = new FetchAccountApi();
    this.page = new FetchPageApi();
    this.pageType = new FetchPageTypeApi();
    this.site = new FetchSiteApi();
    this.snippet = new FetchSnippetApi();
    this.snippetType = new FetchSnippetTypeApi();
  }
}
