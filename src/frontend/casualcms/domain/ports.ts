import { Result } from "neverthrow";
import { Account, PartialPageTemplate } from "./model";

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
}
