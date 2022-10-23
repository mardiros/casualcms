import { Descendant, Editor, Text } from "slate";
import { escapeHtml } from "./strutil";

import { NodeType, SlateModel, TypedLeaf, TypedNode } from "./types";

const serializeNode = (type: NodeType, el: Editor): string => {
  switch (type) {
    case "h1":
      return `<h1>${toHtml(el.children)}</h1>`;
    case "h2":
      return `<h2>${toHtml(el.children)}</h2>`;
    case "h3":
      return `<h3>${toHtml(el.children)}</h3>`;
    case "h4":
      return `<h4>${toHtml(el.children)}</h4>`;
    case "h5":
      return `<h5>${toHtml(el.children)}</h5>`;
    case "h6":
      return `<h6>${toHtml(el.children)}</h6>`;
    case "ul":
      return `<ul>${toHtml(el.children)}</ul>`;
    case "ol":
      return `<ol>${toHtml(el.children)}</ol>`;
    case "li":
      return `<li>${toHtml(el.children)}</li>`;
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
  if (el.italic) {
    html = `<em>${html}</em>`;
  }
  if (el.underline) {
    html = `<u>${html}</u>`;
  }
  if (el.strikethrough) {
    html = `<s>${html}</s>`;
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
