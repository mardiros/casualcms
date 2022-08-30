import {
  IAccountApi,
  IPageApi,
  ISiteApi,
  ISnippetApi,
  IPageTypeApi,
  ISnippetTypeApi,
  ISettingTypeApi,
  ISettingApi,
} from "../domain/ports";
import { FetchAccountApi } from "../adapters/api/account";
import { FetchPageTypeApi } from "../adapters/api/page_type";
import { FetchPageApi } from "../adapters/api/page";
import { FetchSiteApi } from "../adapters/api/site";
import { FetchSnippetApi } from "../adapters/api/snippet";
import { FetchSnippetTypeApi } from "../adapters/api/snippet_type";
import { FetchSettingApi } from "../adapters/api/setting";
import { FetchSettingTypeApi } from "../adapters/api/setting_type";

export interface IApi {
  account: IAccountApi;
  pageType: IPageTypeApi;
  page: IPageApi;
  site: ISiteApi;
  snippet: ISnippetApi;
  snippetType: ISnippetTypeApi;
  setting: ISettingApi;
  settingType: ISettingTypeApi;
}

export class Api implements IApi {
  account: IAccountApi;
  page: IPageApi;
  pageType: IPageTypeApi;
  site: ISiteApi;
  snippet: ISnippetApi;
  snippetType: ISnippetTypeApi;
  settingType: ISettingTypeApi;
  setting: ISettingApi;

  constructor() {
    this.account = new FetchAccountApi();
    this.page = new FetchPageApi();
    this.pageType = new FetchPageTypeApi();
    this.site = new FetchSiteApi();
    this.snippet = new FetchSnippetApi();
    this.snippetType = new FetchSnippetTypeApi();
    this.setting = new FetchSettingApi();
    this.settingType = new FetchSettingTypeApi();
  }
}
