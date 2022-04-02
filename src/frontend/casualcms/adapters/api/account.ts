import { Result, ok, err } from "neverthrow";

import { ApiError, Credentials, IAccountApi } from "casualcms/domain/ports";
import { Account } from "casualcms/domain/model";

import { FastApiError, BaseFetchApi, castError } from "./base";


class FetchAccountApi extends BaseFetchApi implements IAccountApi {

  async byCredentials(creds: Credentials): Promise<Result<Account, ApiError>> {
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
}

export { FetchAccountApi };
