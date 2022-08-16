import { Result } from "neverthrow";
import {
  Account,
  PartialPageTemplate,
  PageTemplate,
  PartialPage,
  Page,
  PartialSite,
  Site,
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

export interface ITemplateApi {
  listTemplates(
    authntoken: string,
    parentType: string | null
  ): Promise<Result<PartialPageTemplate[], ApiError>>;
  showTemplate(
    authntoken: string,
    tpltype: string
  ): Promise<Result<PageTemplate, ApiError>>;
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
  showSite(
    authntoken: string,
    hostname: string
  ): Promise<Result<Site, ApiError>>;
  deleteSite(
    authntoken: string,
    hostname: string
  ): Promise<Result<boolean, ApiError>>;
  listSites(authntoken: string): Promise<Result<PartialSite[], ApiError>>;
}
