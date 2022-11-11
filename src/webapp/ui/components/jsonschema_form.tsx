import React from "react";
import { RJSFSchema, UiSchema } from "@rjsf/utils";
import validator from "@rjsf/validator-ajv6";
import { IChangeEvent, withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { CodeEditor } from "./code/component";
import { RichTextEditor } from "./richtext/component";

const RjsfForm = withTheme(ChakraUITheme);
const widgets = {
  richtext: RichTextEditor,
  code: CodeEditor,
};

type FormProps<T = any, F = any> = {
  schema: RJSFSchema;
  uiSchema: UiSchema;
  formData: T;
  onSubmit: (data: IChangeEvent<T, F>, event: React.FormEvent<any>) => void;
};

export const Form: React.FunctionComponent<FormProps<any>> = (
  props: FormProps
) => {
  const { schema, uiSchema, formData, onSubmit } = props;
  return (
    <RjsfForm
      schema={schema}
      uiSchema={uiSchema}
      formData={formData}
      widgets={widgets}
      validator={validator}
      // onChange={() => console.log("changed")}
      onSubmit={onSubmit}
      // onError={() => console.log("errors")}
    />
  );
};
