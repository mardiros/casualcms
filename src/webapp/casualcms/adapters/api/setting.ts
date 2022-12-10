import { ok, err } from "neverthrow";

import { BaseFetchApi, castError, FastApiError } from "./base";
import { PartialSetting, Payload, Setting } from "../../domain/model";
import { ApiError, AsyncApiResult, ISettingApi } from "../../domain/ports";

export class FetchSettingApi extends BaseFetchApi implements ISettingApi {
  async createSetting(
    authntoken: string,
    hostname: string,
    key: string,
    payload: Payload,
  ): AsyncApiResult<boolean> {
    const setting = {
      key: key,
      payload: payload,
    };
    const response = await this.fetch(`/api/settings/${hostname}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(setting),
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }
  async listSettings(
    authntoken: string,
    hostname: string,
  ): AsyncApiResult<PartialSetting[]> {
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
  async showSetting(
    authntoken: string,
    hostname: string,
    key: string,
  ): AsyncApiResult<Setting> {
    const response = await this.fetch(`/api/settings/${hostname}/${key}`, {
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
    return ok(jsonData as Setting);
  }

  async updateSetting(authntoken: string, setting: Setting): AsyncApiResult<boolean> {
    const response = await this.fetch(
      `/api/settings/${setting.metadata.hostname}/${setting.metadata.key}`,
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${authntoken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(setting),
      },
    );
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }

  async deleteSetting(authntoken: string, setting: Setting): AsyncApiResult<boolean> {
    const response = await this.fetch(
      `/api/settings/${setting.metadata.hostname}/${setting.metadata.key}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${authntoken}`,
        },
      },
    );
    if (!response.ok) {
      const jsonData = await (response.json() as unknown);
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }
}
