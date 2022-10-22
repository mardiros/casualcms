import { NodeType, SlateModel, TypedNode } from "./model";
const NODE_TYPE_TEXT = 3;

export const createTextNode = (content: string | null): TypedNode => {
  return { type: "TEXT", text: content || "" };
};

export const createNode = (
  type: NodeType,
  children: TypedNode[] = [{ type: "TEXT", text: "" }],
  attrs?: { [key: string]: any }
): TypedNode => {
  if (type == "TEXT") {
    return { type: "TEXT", text: "" };
  }
  return {
    type: type,
    attrs: attrs || {},
    children: children,
  };
};

const deserializeNode = (el: ChildNode): TypedNode => {
  if (el.nodeType == NODE_TYPE_TEXT) {
    return createTextNode(el.textContent);
  }

  switch (el.nodeName) {
    case "P":
      return createNode("paragraph", deserializeChildNodes(el));
    case "B":
    case "STRONG":
      return createNode("strong", deserializeChildNodes(el));
  }
  return createTextNode("");
};

const deserializeChildNodes = (el: ChildNode): TypedNode[] => {
  if (!el.hasChildNodes()) {
    return [createTextNode(el.textContent)];
  }

  const nodes: TypedNode[] = [];
  el.childNodes.forEach((e) => nodes.push(deserializeNode(e)));
  return nodes;
};

//   // A: (el) => ({
//   //   type: "link",
//   //   attrs: {
//   //     url: el.getAttribute("href"),
//   //     openInNewTab: el.getAttribute("target") === "_blank",
//   //   },
//   // }),
//   BLOCKQUOTE: () => createNode("block-quote"),
//   H1: () => ({ type: "heading1" }),
//   H2: () => ({ type: "heading2" }),
//   H3: () => ({ type: "heading3" }),
//   H4: () => ({ type: "heading4" }),
//   H5: () => ({ type: "heading5" }),
//   H6: () => ({ type: "heading6" }),
//   IMG: (el) => ({
//     type: "image",
//     url: el.getAttribute("src"),
//     alt: el.getAttribute("alt"),
//   }),
//   LI: () => ({ type: "list-item" }),
//   OL: () => ({ type: "numbered-list" }),
//   P: () => ({ type: "paragraph" }),
//   PRE: () => ({ type: "pre" }),
//   UL: () => ({ type: "bulleted-list" }),
// };

export const defaultModel = (): SlateModel => {
  return [createNode("paragraph")];
};

export const fromHtml = (html: string): SlateModel => {
  if (!html || html.trim().length === 0) {
    return defaultModel();
  }

  // parse html into a DOM document
  const document = new DOMParser().parseFromString(html, "text/html");
  const nodes: SlateModel = [];
  document.body.childNodes.forEach((node) => {
    nodes.push(deserializeNode(node));
  });
  return nodes;

  // // deserialize DOM document into an array of nodes
  // const nodes: SlateModel = deserialize(document.body);

  // // normalize nodes to Slate compatible format
  // nodes.forEach((node) => normalize(node));

  // return nodes;
};
