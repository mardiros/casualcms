import { NodeType, SlateModel, TypedLeaf, TypedNode } from "./types";
const NODE_TYPE_TEXT = 3;

export const createLeaf = (
  text: string | null,
  attrs?: { [key: string]: any }
): TypedLeaf => {
  return {
    bold: attrs?.bold,
    text: text || "",
  };
};

export const createNode = (
  type: NodeType,
  children: SlateModel = []
): TypedNode => {
  return {
    type: type,
    children: children,
  };
};

const deserializeNode = (el: ChildNode): TypedNode | TypedLeaf => {
  if (el.nodeType == NODE_TYPE_TEXT) {
    return createLeaf(el.textContent);
  }

  switch (el.nodeName) {
    case "H1":
      return createNode("h1", deserializeChildNodes(el));
    case "H2":
      return createNode("h2", deserializeChildNodes(el));
    case "P":
      return createNode("paragraph", deserializeChildNodes(el));
    case "B":
    case "STRONG":
      return createLeaf(el.textContent, { bold: true });
  }

  return createLeaf("");
};

const deserializeChildNodes = (el: ChildNode): SlateModel => {
  if (!el.hasChildNodes()) {
    return [createLeaf(el.textContent)];
  }

  const nodes: SlateModel = [];
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
};
