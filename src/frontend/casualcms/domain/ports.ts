import { Result } from "neverthrow";
import { Account } from "./model";

export type ApiError = Map<string, string> | null;

export type Credentials = {
  username: string;
  password: string;
};

export interface IAccountApi {
  byCredentials(creds: Credentials): Promise<Result<Account, ApiError>>;
}
