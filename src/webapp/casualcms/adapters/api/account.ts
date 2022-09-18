import { ok, err } from "neverthrow";

import {
  ApiError,
  AsyncApiResult,
  Credentials,
  IAccountApi,
} from "casualcms/domain/ports";
import { Account } from "casualcms/domain/model";

import { FastApiError, BaseFetchApi, castError } from "./base";

export class FetchAccountApi extends BaseFetchApi implements IAccountApi {
  async byCredentials(creds: Credentials): AsyncApiResult<Account> {
    const response = await this.fetch("/api/authntokens", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(creds),
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as Account);
  }
  async logout(authntoken: string): Promise<boolean> {
    await this.fetch("/api/authntokens", {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${authntoken}`,
      },
    });
    return true;
  }
}
