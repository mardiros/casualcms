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
import {
  BlockButton,
  toggleListBlock,
  toggleMultilineBlock,
} from "./block_btn";
import { LinkButton } from "./popover_button";

export const Toolbar: React.FunctionComponent<{}> = () => {
  return (
    <HStack
      borderWidth={"0 0 1px 0"}
      padding={"10px 5px"}
      spacing={"5px"}
      wrap={"wrap"}
    >
      <MarkButton format="bold" icon={<MdFormatBold />} />
      <MarkButton format="italic" icon={<MdFormatItalic />} />
      <MarkButton format="underline" icon={<MdFormatUnderlined />} />
      <MarkButton format="strikethrough" icon={<MdFormatStrikethrough />} />
      <BlockButton format="h1" icon={<MdLooksOne />} />
      <BlockButton format="h2" icon={<MdLooksTwo />} />
      <BlockButton format="h3" icon={<MdLooks3 />} />
      <BlockButton format="h4" icon={<MdLooks4 />} />
      <BlockButton format="h5" icon={<MdLooks5 />} />
      <BlockButton format="h6" icon={<MdLooks6 />} />
      <BlockButton
        format="ul"
        icon={<MdFormatListBulleted />}
        toggleFn={toggleListBlock}
      />
      <BlockButton
        format="ol"
        icon={<MdFormatListNumbered />}
        toggleFn={toggleListBlock}
      />
      <BlockButton
        format="blockquote"
        icon={<MdFormatQuote />}
        toggleFn={toggleMultilineBlock}
      />
      <BlockButton
        format="code"
        icon={<MdCode />}
        toggleFn={toggleMultilineBlock}
      />
      <LinkButton />
    </HStack>
  );
};
