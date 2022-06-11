import { Result } from "neverthrow";
import { Account, PartialPageTemplate, PageTemplate } from "./model";

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
