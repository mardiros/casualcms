import { Descendant, Editor, Text } from "slate";
import { escapeHtml } from "./strutil";

import { NodeType, SlateModel, TypedLeaf, TypedNode } from "./types";

const serializeNode = (type: NodeType, el: Editor): string => {
  switch (type) {
    case "paragraph":
      return `<p>${serializeNodes(el.children)}</p>`;
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

export const serializeNodes = (els: SlateModel | Descendant[]): string => {
  return els.map((el: any) => {
    return serializeElement(el);
  }).join("");
};

export const toHtml = (mdl: SlateModel): string => {
  return serializeNodes(mdl);
};
