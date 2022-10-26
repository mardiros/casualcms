import React from "react";
import { useSelected, useSlate } from "slate-react";
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

import { MdImage, MdLink } from "react-icons/md";
import {
  EditorProps,
  NodeType,
  TypedLeafImage,
  TypedLink,
  TypedNode,
  TypedText,
} from "../types";
import {
  Editor,
  Transforms,
  Element as SlateElement,
  Range as SlateRange,
  Text as SlateText,
} from "slate";

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
  const editor = useSlate();
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

const ImageFieldSet: React.FunctionComponent<{ onClose: () => void }> = ({
  onClose,
}) => {
  const [imageURL, setImageURL] = React.useState("");
  const [altText, setAltText] = React.useState("");
  const editor = useSlate();

  const onClick = () => {
    const image: TypedLeafImage = {
      type: "image",
      text: imageURL,
      alt: altText,
      id: crypto.randomUUID(),
    };
    Transforms.insertNodes(editor, image);
    onClose();
  };

  return (
    <Stack spacing={2}>
      <InputGroup>
        <FormLabel minWidth="150px">Image URL</FormLabel>
        <Input onChange={(e) => setImageURL(e.currentTarget.value)} />
      </InputGroup>
      <InputGroup>
        <FormLabel textAlign="left" minWidth="150px">
          Alternative text
        </FormLabel>
        <Input onChange={(e) => setAltText(e.currentTarget.value)} />
      </InputGroup>
      <Button variant="solid" size="md" onClick={onClick}>
        Submit
      </Button>
    </Stack>
  );
};

export const ImgButton: React.FunctionComponent<{}> = () => {
  const { onOpen, onClose, isOpen } = useDisclosure();
  return (
    <ModalBox
      format="image"
      icon={<MdImage />}
      onOpen={onOpen}
      onClose={onClose}
      isOpen={isOpen}
    >
      <ImageFieldSet onClose={onClose} />
    </ModalBox>
  );
};

const isLinkActive = (editor: EditorProps) => {
  const [link] = Editor.nodes(editor, {
    match: (n) =>
      !Editor.isEditor(n) &&
      SlateElement.isElement(n) &&
      (n as TypedNode).type === "link",
  });
  return !!link;
};

const unwrapLink = (editor: EditorProps) => {
  let text = "";
  const node = Transforms.unwrapNodes(editor, {
    match: (n) => {
      console.log(n);
      return (
        !Editor.isEditor(n) &&
        SlateElement.isElement(n) &&
        (n as TypedNode).type === "link"
      );
    },
  });
  console.log("#===>");
  console.log(node);
};

// Put this at the start and end of an inline component to work around this Chromium bug:
// https://bugs.chromium.org/p/chromium/issues/detail?id=1249405
const InlineChromiumBugfix = () => (
  <span contentEditable={false} style={{ fontSize: 0 }}>
    ${String.fromCodePoint(160) /* Non-breaking space */}
  </span>
);

const LinkFieldSet: React.FunctionComponent<{
  onClose: () => void;
  href?: string;
}> = ({ onClose, href }) => {
  const editor = useSlate();
  const { selection } = editor;
  const isCollapsed = selection && SlateRange.isCollapsed(selection);

  let defaultText = "";
  if (!isCollapsed) {
    if (href) {
      const nodes = Editor.node(editor, selection as any);
      if (nodes.length) {
        if (SlateText.isText(nodes[0])) {
          defaultText = (nodes[0] as SlateText).text;
        }
      }
    } else {
      defaultText = Editor.string(editor, selection as any);
    }
  }
  const [url, setUrl] = React.useState(href || "");
  const [text, setText] = React.useState(defaultText);

  const onClick = () => {
    const link: TypedLink = {
      type: "link",
      href: url,
      children: [{ type: "TEXT", text }],
    };

    if (isCollapsed) {
      Transforms.insertNodes(editor, [
        link,
        { type: "TEXT", text: " " } as any,
      ]);
    } else {
      Transforms.wrapNodes(editor, link as any, { split: true });
      Transforms.collapse(editor, { edge: "end" });
    }

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
            value={text}
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
  const editor = useSlate();
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
        onClick={onOpen}
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
    </span>
  );
};
