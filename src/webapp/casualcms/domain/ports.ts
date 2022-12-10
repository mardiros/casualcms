import { Result } from "neverthrow";
import {
  Account,
  PartialPageType,
  PageType,
  PartialDraft,
  Draft,
  PartialSite,
  Site,
  PartialSnippet,
  PartialSnippetType,
  SnippetType,
  Snippet,
  PartialSettingType,
  PartialSetting,
  Setting,
  SettingType,
  Payload,
} from "./model";

export type ApiError = Map<string, string> | null;
export type ApiResult<T> = Result<T, ApiError>;
export type AsyncApiResult<T> = Promise<ApiResult<T>>;

export type Credentials = {
  username: string;
  password: string;
};

export interface IAccountApi {
  byCredentials(creds: Credentials): AsyncApiResult<Account>;
  logout(authntoken: string): Promise<boolean>;
}

export interface IPageTypeApi {
  listPageTypes(
    authntoken: string,
    parentType: string | null
  ): AsyncApiResult<PartialPageType[]>;
  showPageType(authntoken: string, pageType: string): AsyncApiResult<PageType>;
}

export interface IPageApi {
  createDraft(
    authntoken: string,
    type: string,
    payload: Payload,
    parent: string | null
  ): AsyncApiResult<boolean>;
  listDrafts(
    authntoken: string,
    parent: string | null
  ): AsyncApiResult<PartialDraft[]>;
  showDraft(authntoken: string, path: string): AsyncApiResult<Draft>;
  previewDraft(authntoken: string, path: string): AsyncApiResult<string>;
  updateDraft(
    authntoken: string,
    path: string,
    page: Draft
  ): AsyncApiResult<Draft>;
  publishPage(
    authntoken: string,
    hostname: string,
    path: string
  ): AsyncApiResult<boolean>;
  deleteDraft(authntoken: string, path: string): AsyncApiResult<boolean>;
}

export type SiteOption = {
  default: boolean;
  secure: boolean;
  root_page_path: string;
};

export interface ISiteApi {
  createSite(
    authntoken: string,
    hostname: string,
    payload: SiteOption
  ): AsyncApiResult<PartialSite>;
  listSites(authntoken: string): AsyncApiResult<PartialSite[]>;
  showSite(authntoken: string, hostname: string): AsyncApiResult<Site>;
  updateSite(
    authntoken: string,
    hostname: string,
    site: Site
  ): AsyncApiResult<boolean>;
  deleteSite(authntoken: string, hostname: string): AsyncApiResult<boolean>;
}

export interface ISnippetApi {
  createSnippet(
    authntoken: string,
    type: string,
    payload: Payload
  ): AsyncApiResult<boolean>;
  listSnippets(authntoken: string): AsyncApiResult<PartialSnippet[]>;
  showSnippet(authntoken: string, slug: string): AsyncApiResult<Snippet>;
  updateSnippet(
    authntoken: string,
    slug: string,
    snippet: Snippet
  ): AsyncApiResult<boolean>;
  deleteSnippet(authntoken: string, snippet: Snippet): AsyncApiResult<boolean>;
}

export interface ISnippetTypeApi {
  listSnippetTypes(authntoken: string): AsyncApiResult<PartialSnippetType[]>;
  showSnippetType(
    authntoken: string,
    snippetType: string
  ): AsyncApiResult<SnippetType>;
}

export interface ISettingTypeApi {
  listSettingTypes(authntoken: string): AsyncApiResult<PartialSettingType[]>;
  showSettingType(authntoken: string, key: string): AsyncApiResult<SettingType>;
}

export interface ISettingApi {
  createSetting(
    authntoken: string,
    hostname: string,
    key: string,
    payload: Payload
  ): AsyncApiResult<boolean>;
  listSettings(
    authntoken: string,
    hostname: string
  ): AsyncApiResult<PartialSetting[]>;
  showSetting(
    authntoken: string,
    hostname: string,
    key: string
  ): AsyncApiResult<Setting>;
  updateSetting(authntoken: string, setting: Setting): AsyncApiResult<boolean>;
  deleteSetting(authntoken: string, setting: Setting): AsyncApiResult<boolean>;
}
