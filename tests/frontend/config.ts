import { err, ok, Result } from "neverthrow";
import {
  Account,
  PartialPageTemplate,
  PageTemplate,
} from "../../src/frontend/casualcms/domain/model";
import {
  ApiError,
  IAccountApi,
  Credentials,
  ITemplateApi,
  IPageApi,
} from "../../src/frontend/casualcms/domain/ports";
import { IApi } from "../../src/frontend/casualcms/service/api";
import { AppConfig } from "../../src/frontend/config";
import { IUnitOfWork } from "../../src/frontend/casualcms/service/uow";
import { IAccountRepository } from "../../src/frontend/casualcms/domain/repositories";
import { m } from "framer-motion";

class FakeAccountApi implements IAccountApi {
  async byCredentials(creds: Credentials): Promise<Result<Account, ApiError>> {
    if (creds.password == "justincase") {
      let errMap = new Map();
      errMap.set("username", "Invalid username or password");
      return err(errMap);
    }
    return ok({
      id: "123",
      token: "abc123",
      lang: "en",
      username: creds.username,
    });
  }
}

class FakeTemplateApi implements ITemplateApi {
  async listRoots(
    authntoken: string
  ): Promise<Result<Array<PartialPageTemplate>, Map<string, string>>> {
    return ok([
      {
        type: "casual:Home",
      },
    ]);
  }
  async showTemplate(
    authntoken: string,
    tpltype: string
  ): Promise<Result<PageTemplate, ApiError>> {
    if (tpltype != "blog:HomePage") {
      let m = new Map();
      m.set("detail", `${tpltype} is undefined`);
      return err(m);
    }
    return ok({
      uiSchema: {
        id: { "ui:widget": "hidden" },
        slug: { "ui:widget": "text" },
        hero_title: { "ui:widget": "text" },
        title: { "ui:widget": "text" },
        description: { "ui:widget": "text" },
        body: { "ui:widget": "text" },
      },
      schema: {
        title: "HomePage",
        type: "object",
        properties: {
          id: { title: "Id", type: "string" },
          slug: { title: "Slug", type: "string" },
          title: { title: "Title", type: "string" },
          description: { title: "Description", type: "string" },
          body: { title: "Body", type: "string" },
        },
        required: ["id", "slug", "title", "description", "body"],
        definitions: {},
      },
    });
  }
}

class FakePageApi implements IPageApi {
  async createRootPage(
    authntoken: string,
    type: string,
    payload: any
  ): Promise<Result<boolean, Map<string, string>>> {
      return ok(true);
  }
}

class FakeApi implements IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;

  constructor() {
    this.account = new FakeAccountApi();
    this.template = new FakeTemplateApi();
    this.page = new FakePageApi();
  }
}

class FakeAccountRepository implements IAccountRepository {
  account: Result<Account, string>;

  constructor() {
    this.account = err("No account");
  }
  async getCurrent(): Promise<Result<Account, string>> {
    return this.account;
  }
  async set(model: Account): Promise<boolean> {
    this.account = ok(model);
    return true;
  }
}

class FakeUnitOfWork implements IUnitOfWork {
  account: IAccountRepository;

  constructor() {
    this.account = new FakeAccountRepository();
  }
}

const cfg = new AppConfig(new FakeUnitOfWork(), new FakeApi());

export default cfg;
