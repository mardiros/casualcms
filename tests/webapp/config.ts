import { err, ok, Result } from "neverthrow";
import {
  Account,
  PartialPageTemplate,
  PageTemplate,
  PartialPage,
} from "../../src/webapp/casualcms/domain/model";
import {
  ApiError,
  IAccountApi,
  Credentials,
  ITemplateApi,
  IPageApi,
} from "../../src/webapp/casualcms/domain/ports";
import { IApi } from "../../src/webapp/casualcms/service/api";
import { AppConfig } from "../../src/webapp/config";
import { IUnitOfWork } from "../../src/webapp/casualcms/service/uow";
import { IAccountRepository } from "../../src/webapp/casualcms/domain/repositories";
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
        slug: { "ui:widget": "hidden" },
        title: { "ui:widget": "text", "ui:placeholder": "title" },
        body: { "ui:widget": "text", "ui:placeholder": "body" },
      },
      schema: {
        title: "HomePage",
        type: "object",
        properties: {
          id: { title: "Id", type: "string" },
          slug: { title: "Slug", type: "string" },
          title: { title: "Title", type: "string" },
          body: { title: "Body", type: "string" },
        },
        required: ["id", "slug", "title", "body"],
        definitions: {},
      },
    });
  }
}

class FakePageApi implements IPageApi {
  pages: Array<any>;

  constructor() {
    this.pages = [];
  }
  async createRootPage(
    authntoken: string,
    type: string,
    payload: any
  ): Promise<Result<boolean, Map<string, string>>> {
    this.pages.push(payload);
    return ok(true);
  }

  async listRoots(
    authntoken: string
  ): Promise<Result<PartialPage[], Map<string, string>>> {
    let roots: PartialPage[] = [];
    this.pages
      .filter((page) => page.slug == "/")
      .map((page) => roots.push({ slug: page.slug, title: page.title }));
    return ok(roots);
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
