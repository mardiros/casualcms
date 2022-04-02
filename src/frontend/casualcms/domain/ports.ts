import { Result } from "neverthrow";
import { Account } from "./model";

type ApiError = Map<string, string> | null;

type Credentials = {
  username: string;
  password: string;
};

interface IAccountApi {
  byCredentials(creds: Credentials): Promise<Result<Account, ApiError>>;
}

export type {
  // FastAPI error format
  ApiError,
  Credentials,
  IAccountApi,
};
