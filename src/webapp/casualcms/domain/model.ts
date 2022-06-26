import { JSONSchema7 } from "json-schema";

export type Account = {
  id: string;
  username: string;
  token: string;
  lang: string;
};


export type PartialPageTemplate = {
  type: string;
}

export type PageTemplate = {
  // type:string;
  schema:JSONSchema7;
  uiSchema: any;
}
