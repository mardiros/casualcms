import { Box } from "@chakra-ui/react";
import Form from "@rjsf/chakra-ui";
import { JSONSchema7 } from "json-schema";

export const PageEdit: React.FunctionComponent<{}> = () => {
  const schema: JSONSchema7 = {
    "definitions": {
      "Paragraph": {
        "properties": {
          "body": { "title": "Body", "type": "string" },
          "title": { "title": "Title", "type": "string" },
        },
        "required": ["body"],
        "title": "Paragraph",
        "type": "object",
      }
    },
    "properties": {
      "body": {
        "title": "Body",
        "type": "array",
        "default": [],
        "items": { "$ref": "#/definitions/Paragraph" },
      },
      "description": { "title": "Description", "type": "string" },
      "hero_title": {
        "title": "Hero Title",
        "type": "string",
        "description": "Title of the hero section",
      },
      "id": { "title": "Id", "type": "string" },
      "slug": { "title": "Slug", "type": "string" },
      "title": { "title": "Title", "type": "string" },
    },
    "required": ["id", "slug", "title", "description", "hero_title"],
    "title": "RootPage",
    "type": "object",
  }
  return <Box maxW="720px">
    <Form schema={schema}
        onChange={() =>console.log("changed")}
        onSubmit={() =>console.log("submitted")}
        onError={() =>console.log("errors")} />
  </Box>
}
