import React from "react";
import { Editor } from "slate";
import { useSlate } from "slate-react";
import { IconButton } from "@chakra-ui/react";

import { EditorProps, TypedText } from "../types";

const isMarkActive = (editor: EditorProps, format: string) => {
  const marks = Editor.marks(editor);
  if (marks) {
    const myMarks = marks as TypedText;
    const myFormat = format as keyof TypedText;
    return myMarks[myFormat] === true;
  }
  return false;
};

export const toggleMark = (editor: EditorProps, format: string): void => {
  const isActive = isMarkActive(editor, format);
  if (isActive) {
    Editor.removeMark(editor, format);
  } else {
    Editor.addMark(editor, format, true);
  }
};

export const MarkButton = ({
  format,
  icon,
}: {
  format: string;
  icon: React.ReactElement;
}) => {
  const editor = useSlate();
  return (
    <IconButton
      variant="outline"
      colorScheme="blue"
      isActive={isMarkActive(editor, format)}
      onMouseDown={(event) => {
        event.preventDefault();
        toggleMark(editor, format);
      }}
      aria-label={format}
      icon={icon}
      borderWidth={0}
      fontSize={"20px"}
    />
  );
};
