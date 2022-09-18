import { ok, err } from "neverthrow";

import { BaseFetchApi, castError, FastApiError } from "./base";
import { PartialSettingType, SettingType } from "../../domain/model";
import { ApiError, AsyncApiResult, ISettingTypeApi } from "../../domain/ports";

export class FetchSettingTypeApi
  extends BaseFetchApi
  implements ISettingTypeApi
{
  async listSettingTypes(
    authntoken: string
  ): AsyncApiResult<PartialSettingType[]> {
    const response = await this.fetch("/api/settings-types", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        Accept: "application/json",
      },
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as PartialSettingType[]);
  }
  async showSettingType(
    authntoken: string,
    key: string
  ): AsyncApiResult<SettingType> {
    const response = await this.fetch(`/api/settings-types/${key}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        Accept: "application/json",
      },
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as SettingType);
  }
}
