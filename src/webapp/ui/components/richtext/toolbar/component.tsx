import React from "react";
import { HStack } from "@chakra-ui/react";

import {
  MdCode,
  MdFormatBold,
  MdFormatItalic,
  MdFormatListBulleted,
  MdFormatListNumbered,
  MdFormatQuote,
  MdFormatStrikethrough,
  MdFormatUnderlined,
  MdLooks3,
  MdLooks4,
  MdLooks5,
  MdLooks6,
  MdLooksOne,
  MdLooksTwo,
} from "react-icons/md";
import { MarkButton } from "./mark_btn";
import { BlockButton, toggleListBlock, toggleMultilineBlock } from "./block_btn";
import { LinkButton } from "./popover_button";
import { FeatureType } from "../types";

type FunctionComponentProps = {
  features: FeatureType[];
};

export const Toolbar: React.FunctionComponent<FunctionComponentProps> = ({
  features,
}: FunctionComponentProps) => {
  const buttons: Record<FeatureType, JSX.Element> = {
    bold: <MarkButton format="bold" icon={<MdFormatBold />} />,
    italic: <MarkButton format="italic" icon={<MdFormatItalic />} />,
    underline: <MarkButton format="underline" icon={<MdFormatUnderlined />} />,
    strikethrough: (
      <MarkButton format="strikethrough" icon={<MdFormatStrikethrough />} />
    ),
    h1: <BlockButton format="h1" icon={<MdLooksOne />} />,
    h2: <BlockButton format="h2" icon={<MdLooksTwo />} />,
    h3: <BlockButton format="h3" icon={<MdLooks3 />} />,
    h4: <BlockButton format="h4" icon={<MdLooks4 />} />,
    h5: <BlockButton format="h5" icon={<MdLooks5 />} />,
    h6: <BlockButton format="h6" icon={<MdLooks6 />} />,
    ul: (
      <BlockButton
        format="ul"
        icon={<MdFormatListBulleted />}
        toggleFn={toggleListBlock}
      />
    ),
    ol: (
      <BlockButton
        format="ol"
        icon={<MdFormatListNumbered />}
        toggleFn={toggleListBlock}
      />
    ),
    blockquote: (
      <BlockButton
        format="blockquote"
        icon={<MdFormatQuote />}
        toggleFn={toggleMultilineBlock}
      />
    ),
    code: (
      <BlockButton format="code" icon={<MdCode />} toggleFn={toggleMultilineBlock} />
    ),
    link: <LinkButton />,
    paragraph: <></>,
    li: <></>,
  };
  return (
    <HStack
      borderWidth={"0 0 1px 0"}
      padding={"10px 5px"}
      spacing={"5px"}
      wrap={"wrap"}
    >
      {features.map((feat: FeatureType) => {
        return <React.Fragment key={feat}>{buttons[feat]}</React.Fragment>;
      })}
    </HStack>
  );
};
