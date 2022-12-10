import React from "react";
import { Element } from "slate";
import { RenderElementProps, RenderLeafProps, useSlate } from "slate-react";
import {
  chakra,
  ListItem,
  OrderedList,
  UnorderedList,
  Heading,
} from "@chakra-ui/react";

import { NodeType, TypedText, TypedLink } from "./types";
import { InlineLink } from "./toolbar/popover_button";

export interface MyElement extends Element {
  type: NodeType;
}

export interface MyRenderElementProps extends RenderElementProps {
  element: MyElement;
}

export interface MyRenderLeafProps extends RenderLeafProps {
  leaf: TypedText;
}

export const MyRenderElement = ({
  attributes,
  children,
  element,
}: MyRenderElementProps) => {
  // console.log(`Render Element ${element.type}`);
  switch (element.type) {
    case "h1":
      return (
        <Heading as="h1" size="3xl" {...attributes}>
          {children}
        </Heading>
      );
    case "h2":
      return (
        <Heading as="h2" size="2xl" {...attributes}>
          {children}
        </Heading>
      );
    case "h3":
      return (
        <Heading as="h3" size="xl" {...attributes}>
          {children}
        </Heading>
      );
    case "h4":
      return (
        <Heading as="h4" size="lg" {...attributes}>
          {children}
        </Heading>
      );
    case "h5":
      return (
        <Heading as="h5" size="sd" {...attributes}>
          {children}
        </Heading>
      );
    case "h6":
      return (
        <Heading as="h6" size="sm" {...attributes}>
          {children}
        </Heading>
      );
    case "ul":
      return <UnorderedList {...attributes}>{children}</UnorderedList>;
    case "ol":
      return <OrderedList {...attributes}>{children}</OrderedList>;
    case "li":
      return <ListItem {...attributes}>{children}</ListItem>;
    case "code":
      return (
        <chakra.blockquote
          padding={"3px"}
          backgroundColor={"gray.200"}
          fontFamily={"monospace"}
        >
          {children}
        </chakra.blockquote>
      );
    case "blockquote":
      return (
        <chakra.blockquote
          borderLeftWidth={"10px"}
          borderLeftColor={"gray.200"}
          fontFamily={"serif"}
          {...attributes}
        >
          {children}
        </chakra.blockquote>
      );

    case "link":
      const link = element as TypedLink;
      return (
        <InlineLink href={link.href} slate_attributes={attributes}>
          {children}
        </InlineLink>
      );
    case "paragraph":
      return <p {...attributes}>{children}</p>;

    default:
      return <div {...attributes}>{children}</div>;
  }
};

export const MyRenderLeaf = ({ attributes, children, leaf }: MyRenderLeafProps) => {
  const editor = useSlate();
  switch (leaf.type) {
    case "TEXT":
      const txt = leaf as TypedText;
      if (txt.bold) {
        children = <strong>{children}</strong>;
      }
      if (txt.italic) {
        children = <em>{children}</em>;
      }
      if (txt.underline) {
        children = <u>{children}</u>;
      }
      if (txt.strikethrough) {
        children = <s>{children}</s>;
      }
      return <span {...attributes}>{children}</span>;
  }
  return <></>;
};
