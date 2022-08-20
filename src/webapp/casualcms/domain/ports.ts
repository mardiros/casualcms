import { Result } from "neverthrow";
import {
  Account,
  PartialPageType,
  PageType,
  PartialPage,
  Page,
  PartialSite,
  Site,
  PartialSnippet,
  PartialSnippetType,
  SnippetType,
  Snippet,
} from "./model";

export type ApiError = Map<string, string> | null;

export type Credentials = {
  username: string;
  password: string;
};

export interface IAccountApi {
  byCredentials(creds: Credentials): Promise<Result<Account, ApiError>>;
  logout(authntoken: string): Promise<boolean>;
}

export interface IPageTypeApi {
  listPageTypes(
    authntoken: string,
    parentType: string | null
  ): Promise<Result<PartialPageType[], ApiError>>;
  showPageType(
    authntoken: string,
    pageType: string
  ): Promise<Result<PageType, ApiError>>;
}

export interface IPageApi {
  createPage(
    authntoken: string,
    type: string,
    payload: any,
    parent: string | null
  ): Promise<Result<boolean, ApiError>>;
  listPages(
    authntoken: string,
    parent: string | null
  ): Promise<Result<PartialPage[], ApiError>>;
  showPage(authntoken: string, path: string): Promise<Result<Page, ApiError>>;
  updatePage(
    authntoken: string,
    path: string,
    page: Page
  ): Promise<Result<Page, ApiError>>;
  deletePage(
    authntoken: string,
    path: string
  ): Promise<Result<boolean, ApiError>>;
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
  ): Promise<Result<PartialSite, ApiError>>;
  listSites(authntoken: string): Promise<Result<PartialSite[], ApiError>>;
  showSite(
    authntoken: string,
    hostname: string
  ): Promise<Result<Site, ApiError>>;
  deleteSite(
    authntoken: string,
    hostname: string
  ): Promise<Result<boolean, ApiError>>;
}

export interface ISnippetApi {
  createSnippet(
    authntoken: string,
    type: string,
    payload: any
  ): Promise<Result<boolean, ApiError>>;
  listSnippets(authntoken: string): Promise<Result<PartialSnippet[], ApiError>>;
  showSnippet(
    authntoken: string,
    slug: string
  ): Promise<Result<Snippet, ApiError>>;
  updateSnippet(
    authntoken: string,
    slug: string,
    snippet: Snippet
  ): Promise<Result<boolean, ApiError>>;
  deleteSnippet(
    authntoken: string,
    snippet: Snippet
  ): Promise<Result<boolean, ApiError>>;
}

export interface ISnippetTypeApi {
  listSnippetTypes(
    authntoken: string
  ): Promise<Result<PartialSnippetType[], ApiError>>;
  showSnippetType(
    authntoken: string,
    snippetType: string
  ): Promise<Result<SnippetType, ApiError>>;
}
