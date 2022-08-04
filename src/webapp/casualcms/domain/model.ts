import { JSONSchema7 } from "json-schema";

export type Account = {
  id: string;
  username: string;
  token: string;
  lang: string;
};

export type PartialPageTemplate = {
  type: string;
};

export type PageTemplate = {
  // type:string;
  schema: JSONSchema7;
  uiSchema: any;
};

export type PartialPageMeta = {
  path: string;
  type: string;
};

export type PartialPage = {
  slug: string;
  title: string;
  meta: PartialPageMeta;
};

export type Page = {
  meta: PartialPageMeta;
  [k: string]: any;
};
