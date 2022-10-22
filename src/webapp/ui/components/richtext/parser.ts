import { TypedNode } from "./model";
import { Node } from "slate";

type SlateModel = Array<Node & TypedNode>;

export const emptyModel = (): SlateModel => {
  return [
    {
      type: "paragraph",
      children: [{ text: "" }],
    },
  ];
};

export const fromHtml = (html: string): SlateModel => {
  if (!html || html.trim().length === 0) {
    return emptyModel();
  }

  return [];
};
