import { Descendant, Text } from "slate";
import { escapeHtml } from "./strutil";

import {
  NodeType,
  SlateModel,
  TypedLeaf,
  TypedLeafImage,
  TypedLink,
  TypedNode,
  TypedText,
} from "./types";

const serializeNode = (type: NodeType, el: TypedNode): string => {
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
    case "code":
      return `<pre>${toHtml(el.children)}</pre>`;
    case "blockquote":
      return `<blockquote>${toHtml(el.children)}</blockquote>`;
    case "paragraph":
      // render paragraph as div while editing...
      return `<p>${toHtml(el.children)}</p>`;

    case "link":
      // render paragraph as div while editing...
      return `<a href="${escapeHtml((el as TypedLink).href)}">${toHtml(
        el.children
      )}</a>`;

    // case "image":
    //   const attrs = (el as TypedNode).attrs;
    //   return `<img src="${attrs?.src}" alt="${attrs?.alt}" />`;
  }
  return "";
};

const serializeLeaf = (el: TypedLeaf): string => {
  switch (el.type) {
    case "image":
      const img = el as TypedLeafImage;
      return `<img src="${el.text}" alt="${img.alt}" />`;
    case "TEXT":
      const txt = el as TypedText;
      let html = escapeHtml(el.text);
      if (txt.bold) {
        html = `<strong>${html}</strong>`;
      }
      if (txt.italic) {
        html = `<em>${html}</em>`;
      }
      if (txt.underline) {
        html = `<u>${html}</u>`;
      }
      if (txt.strikethrough) {
        html = `<s>${html}</s>`;
      }
      return html;
  }
  return "";
};

const serializeElement = (el: TypedNode | TypedLeaf): string => {
  if (Text.isText(el)) {
    return serializeLeaf(el);
  } else {
    return serializeNode(el.type, el);
  }
};

export const toHtml = (els: SlateModel | Descendant[]): string => {
  return els
    .map((el: any) => {
      return serializeElement(el);
    })
    .join("");
};
