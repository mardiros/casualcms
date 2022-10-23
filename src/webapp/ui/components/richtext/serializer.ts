import { Descendant, Editor, Text } from "slate";
import { escapeHtml } from "./strutil";

import { NodeType, SlateModel, TypedLeaf, TypedNode } from "./types";

const serializeNode = (type: NodeType, el: Editor): string => {
  switch (type) {
    case "h1":
      return `<h1>${toHtml(el.children)}</h1>`;
    case "h2":
      return `<h2>${toHtml(el.children)}</h2>`;
    case "paragraph":
      return `<p>${toHtml(el.children)}</p>`;
  }
  return "";
};

const serializeLeaf = (el: TypedLeaf): string => {
  let html = escapeHtml(el.text);
  if (el.bold) {
    html = `<strong>${html}</strong>`;
  }
  return html;
};

const serializeElement = (el: TypedNode | TypedLeaf): string => {
  if (Text.isText(el)) {
    return serializeLeaf(el);
  } else {
    return serializeNode(el.type, el as Editor);
  }
};

export const toHtml = (els: SlateModel | Descendant[]): string => {
  return els
    .map((el: any) => {
      return serializeElement(el);
    })
    .join("");
};
