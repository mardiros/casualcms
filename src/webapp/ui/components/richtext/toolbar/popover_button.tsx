import React from "react";
import { useSelected } from "slate-react";
import {
  IconButton,
  useDisclosure,
  Button,
  InputGroup,
  Input,
  Stack,
  FormLabel,
  Text,
  AlertDialog,
  AlertDialogOverlay,
  AlertDialogContent,
} from "@chakra-ui/react";

import { MdLink } from "react-icons/md";
import { MyEditor, NodeType, TypedLink } from "../types";
import {
  Editor,
  Transforms,
  Element as SlateElement,
  Range as SlateRange,
  Text as SlateText,
} from "slate";
import { useMyEditor } from "../hooks";

type ModalBoxProps = {
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
  format: NodeType;
  icon: React.ReactElement;
  isActive?: boolean;
  children: React.ReactNode;
};

const ModalBox: React.FunctionComponent<ModalBoxProps> = ({
  isOpen,
  onOpen,
  onClose,
  format,
  icon,
  children,
  isActive,
}) => {
  const cancelRef = React.useRef<any>();
  return (
    <>
      <IconButton
        variant="outline"
        colorScheme="green"
        aria-label={format}
        icon={icon}
        borderWidth={0}
        fontSize={"20px"}
        onClick={onOpen}
        isActive={isActive || false}
      />
      <AlertDialog
        motionPreset="slideInBottom"
        leastDestructiveRef={cancelRef}
        onClose={onClose}
        isOpen={isOpen}
        isCentered
      >
        <AlertDialogOverlay />
        <AlertDialogContent>{children}</AlertDialogContent>
      </AlertDialog>
    </>
  );
};

const isLinkActive = (editor: MyEditor) => {
  const [link] = Editor.nodes(editor, {
    match: (n) =>
      !Editor.isEditor(n) && SlateElement.isElement(n) && n.type === "link",
  });
  return !!link;
};

const unwrapLink = (editor: MyEditor) => {
  Transforms.unwrapNodes(editor, {
    match: (n) => {
      return (
        !Editor.isEditor(n) && SlateElement.isElement(n) && n.type === "link"
      );
    },
  });
};

const wrapLink = (editor: MyEditor, href: string, text: string) => {
  if (isLinkActive(editor)) {
    unwrapLink(editor);
  }

  const { selection } = editor;
  const isCollapsed = selection && SlateRange.isCollapsed(selection);
  const link: TypedLink = {
    type: "link",
    href,
    children: isCollapsed ? [{ type: "TEXT", text }] : [],
  };

  if (isCollapsed) {
    Transforms.insertNodes(editor, link);
  } else {
    Transforms.wrapNodes(editor, link, { split: true });
    Transforms.collapse(editor, { edge: "end" });
  }
};

// Put this at the start and end of an inline component to work around this Chromium bug:
// https://bugs.chromium.org/p/chromium/issues/detail?id=1249405
const InlineChromiumBugfix = () => (
  <span contentEditable={false} style={{ fontSize: 0 }}>
    &nbsp;
  </span>
);

const LinkFieldSet: React.FunctionComponent<{
  onClose: () => void;
  href?: string;
}> = ({ onClose, href }) => {
  const editor = useMyEditor();
  const { selection } = editor;
  const isCollapsed = selection && SlateRange.isCollapsed(selection);

  let defaultText = "";
  if (!isCollapsed) {
    if (href) {
      const nodes = Editor.node(editor, selection as any);
      if (nodes.length) {
        if (SlateText.isText(nodes[0])) {
          defaultText = nodes[0].text;
        }
      }
    } else {
      defaultText = Editor.string(editor, selection as any);
    }
  }
  const [url, setUrl] = React.useState(href || "");
  const [newText, setText] = React.useState(defaultText);

  const onClick = () => {
    wrapLink(editor, url, newText);
    // // If it was a link, we need to rewrite it
    // if (isLinkActive(editor)) {
    //   unwrapLink(editor)
    // }

    // const link: TypedLink = {
    //   type: "link",
    //   href: url,
    //   children: [{ type: "TEXT", text }],
    // };

    // if (isCollapsed) {
    //   console.log(editor.selection)
    //   Transforms.insertNodes(editor,
    //     link,
    //     // { type: "TEXT", text: " " } as any,
    //   );
    // } else {
    //   console.log("//////////////////////////////////////");
    //   Transforms.wrapNodes(editor, link as any, { split: true });
    //   Transforms.collapse(editor, { edge: "end" });
    // }

    setUrl("");
    setText("");
    onClose();
  };

  return (
    <Stack spacing={2} padding={"1.5em"}>
      <InputGroup>
        <FormLabel textAlign="left" minWidth="120px">
          URL
        </FormLabel>
        <Input
          value={url}
          onChange={(e) => setUrl(e.currentTarget.value)}
          minWidth={"250px"}
        />
      </InputGroup>
      {isCollapsed && (
        <InputGroup>
          <FormLabel textAlign="left" minWidth="120px">
            Text Label
          </FormLabel>
          <Input
            value={newText}
            onChange={(e) => setText(e.currentTarget.value)}
            minWidth={"250px"}
          />
        </InputGroup>
      )}
      <Button variant="solid" size="md" onClick={onClick}>
        Submit
      </Button>
    </Stack>
  );
};

export const LinkButton: React.FunctionComponent<{}> = () => {
  const editor = useMyEditor();
  const { onOpen, onClose, isOpen } = useDisclosure();
  return (
    <ModalBox
      format="link"
      icon={<MdLink />}
      onOpen={onOpen}
      onClose={onClose}
      isOpen={isOpen}
      isActive={isLinkActive(editor)}
    >
      <LinkFieldSet onClose={onClose} />
    </ModalBox>
  );
};

type InlineLinkProps = {
  href: string;
  slate_attributes: any;
  children: React.ReactNode;
};
export const InlineLink: React.FunctionComponent<InlineLinkProps> = (
  props: InlineLinkProps
) => {
  const { href, children, slate_attributes } = props;
  const { onOpen, onClose, isOpen } = useDisclosure();
  const cancelRef = React.useRef<any>();
  const selected = useSelected();
  return (
    <span {...slate_attributes}>
      <InlineChromiumBugfix />
      <Text
        as="span"
        color="blue.500"
        display="inline"
        textDecoration="underline"
        boxShadow={selected ? "0 0 0 2px #c0c0e0" : "0"}
      >
        {children}
      </Text>

      <AlertDialog
        motionPreset="slideInBottom"
        onClose={onClose}
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        isCentered
      >
        <AlertDialogOverlay />

        <AlertDialogContent>
          <LinkFieldSet onClose={onClose} href={href} />
        </AlertDialogContent>
      </AlertDialog>
      <InlineChromiumBugfix />
    </span>
  );
};
