import { ArrayFieldTemplateProps } from "@rjsf/core";
import { Result } from "neverthrow";
import {
  Account,
  PartialPageTemplate,
  PageTemplate,
  PartialPage,
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
  listRoots(
    authntoken: string
  ): Promise<Result<Array<PartialPageTemplate>, ApiError>>;
  showTemplate(
    authntoken: string,
    tpltype: string
  ): Promise<Result<PageTemplate, ApiError>>;
}

export interface IPageApi {
  createRootPage(
    authntoken: string,
    type: string,
    payload: any
  ): Promise<Result<boolean, ApiError>>;
  listRoots(authntoken: string): Promise<Result<Array<PartialPage>, ApiError>>;
  listPages(
    authntoken: string,
    parent: string
  ): Promise<Result<Array<PartialPage>, ApiError>>;
}
