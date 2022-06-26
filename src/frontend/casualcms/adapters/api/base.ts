import { ApiError } from "casualcms/domain/ports";

type ApiErrorItem = {
  loc: String[];
  msg: String;
  // type: String
  // ctx: any
};

export type FastApiError = {
  detail: ApiErrorItem[];
};

export const castError = (api_errors: FastApiError): ApiError => {
  let errors = new Map();
  api_errors.detail.forEach((error) => {
    if (errors.has(error.loc[1])) {
      errors.set(error.loc[1], `${errors.get(error.loc[1])}; ${error.msg}`);
    } else {
      errors.set(error.loc[1], error.msg);
    }
  });
  return errors;
};

export class BaseFetchApi {
  _fetch: Function | null;
  constructor(...args: Function[]) {
    if (args.length > 0) {
      this._fetch = args[0];
    } else {
      this._fetch = null;
    }
  }
  fetch = async (req: RequestInfo, ini: RequestInit): Promise<Response> => {
    const fetch_ = this._fetch || fetch;
    return fetch_(req, ini);
  };
}
