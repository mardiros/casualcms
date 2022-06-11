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
} from "../../src/frontend/casualcms/domain/ports";
import { IApi } from "../../src/frontend/casualcms/service/api";
import { AppConfig } from "../../src/frontend/config";
import { IUnitOfWork } from "../../src/frontend/casualcms/service/uow";
import { IAccountRepository } from "../../src/frontend/casualcms/domain/repositories";

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
    return ok({
      schema: {
        definitions: {
          Paragraph: {
            properties: {
              body: { title: "Body", type: "string" },
              title: { title: "Title", type: "string" },
            },
            required: ["body"],
            title: "Paragraph",
            type: "object",
          },
        },
        properties: {
          body: {
            title: "Body",
            type: "array",
            default: [],
            items: { $ref: "#/definitions/Paragraph" },
          },
          description: { title: "Description", type: "string" },
          hero_title: {
            title: "Hero Title",
            type: "string",
            description: "Title of the hero section",
          },
          id: { title: "Id", type: "string" },
          slug: { title: "Slug", type: "string" },
          title: { title: "Title", type: "string" },
        },
        required: ["id", "slug", "title", "description", "hero_title"],
        title: "RootPage",
        type: "object",
      },
    });
  }
}

class FakeApi implements IApi {
  account: IAccountApi;
  template: ITemplateApi;

  constructor() {
    this.account = new FakeAccountApi();
    this.template = new FakeTemplateApi();
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
