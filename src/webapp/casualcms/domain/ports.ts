import { Result } from "neverthrow";
import {
  Account,
  PartialPageTemplate,
  PageTemplate,
  PartialPage,
  Page,
} from "./model";

export type ApiError = Map<string, string> | null;

export type Credentials = {
  username: string;
  password: string;
};

export interface IAccountApi {
  byCredentials(creds: Credentials): Promise<Result<Account, ApiError>>;
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
  deletePage(
    authntoken: string,
    path: string
  ): Promise<Result<boolean, ApiError>>;
}
