import { Result, ok, err } from "neverthrow";

import { BaseFetchApi, castError, FastApiError } from "./base";
import { PartialSetting, Setting } from "../../domain/model";
import { ApiError, ISettingApi } from "../../domain/ports";

export class FetchSettingApi extends BaseFetchApi implements ISettingApi {
  async listSettings(
    authntoken: string,
    hostname: string
  ): Promise<Result<PartialSetting[], ApiError>> {
    const response = await this.fetch(`/api/settings/${hostname}`, {
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
    return ok(jsonData as PartialSetting[]);
  }
  async createSetting(
    authntoken: string,
    hostname: string,
    type: string,
    payload: any
  ): Promise<Result<boolean, ApiError>> {
    const setting: any = {
      meta: { type: type },
      ...payload,
    };
    const response = await this.fetch(`/api/settings/${hostname}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        Accept: "application/json",
      },
      body: JSON.stringify(setting),
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }
  async deleteSetting(
    authntoken: string,
    setting: Setting
  ): Promise<Result<boolean, ApiError>> {
    const response = await this.fetch(
      `/api/settings/${setting.hostname}/${setting.meta.key}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${authntoken}`,
        },
      }
    );
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }
}
