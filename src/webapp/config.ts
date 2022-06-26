import React from "react";
import { IApi } from "casualcms/service/api";
import { IUnitOfWork } from "casualcms/service/uow";

export class AppConfig {
  api: IApi;
  uow: IUnitOfWork;

  constructor(uow: IUnitOfWork, api: IApi) {
    this.api = api;
    this.uow = uow;
  }
}

// The context as to be initialized first before use the app, right!
export const AppContext = React.createContext<AppConfig>(null!);

export function useConfig() {
  return React.useContext(AppContext);
}
