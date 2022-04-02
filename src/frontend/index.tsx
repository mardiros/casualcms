import React from "react";
import ReactDOM from "react-dom";
import { App } from "./App";
import { AppContext, AppConfig } from "./config";
import { initDB } from "./casualcms/adapters/repositories";
import { Api } from "./casualcms/service/api";
import { UnitOfWork } from "./casualcms/service/uow";

import "./css/index.scss";

const init = async (): Promise<AppConfig> => {
  const db = await initDB();
  const config = new AppConfig(new UnitOfWork(db), new Api());
  return config;
};

init().then(async (config: AppConfig) => {
  ReactDOM.render(
    <React.StrictMode>
      <AppContext.Provider value={config}>
        <App />
      </AppContext.Provider>
    </React.StrictMode>,
    document.getElementById("root")
  );
});
