import React from "react";
import { IApi } from "casualcms/service/api";
import { IUnitOfWork } from "casualcms/service/uow";

class AppConfig {
  api: IApi;
  uow: IUnitOfWork;

  constructor(uow: IUnitOfWork, api: IApi) {
    this.api = api;
    this.uow = uow;
  }
}

// The context as to be initialized first before use the app, right!
const AppContext = React.createContext<AppConfig | null>(null);

function useConfig() {
  return React.useContext(AppContext);
}

export { AppContext, AppConfig, useConfig };
