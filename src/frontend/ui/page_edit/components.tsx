import React from "react";
import { Box } from "@chakra-ui/react";
import Form from "@rjsf/chakra-ui";
import { useParams } from 'react-router-dom';
import { useAuth } from "../login/components";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";
import { PageTemplate } from "../../casualcms/domain/model";

export const PageEdit: React.FunctionComponent<{}> = () => {
  let { tpltype } = useParams();
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [template, setTemplate] = React.useState<PageTemplate>(null);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadTemplate() {
      const template = await config.api.template.showTemplate(token, tpltype);
      template.
        map((tpl) => setTemplate(tpl)).
        mapErr((err) => setError(err));
    }
    loadTemplate();
    return function cleanup() { };
  }, []);

  console.log(tpltype)
  console.log("#")
  return <Box maxW="720px">
    {template &&
      <Form schema={template.schema}
        onChange={() => console.log("changed")}
        onSubmit={() => console.log("submitted")}
        onError={() => console.log("errors")} />
    }
    {/* TODO display error properly, just in cases */}
    {
      error &&
      <ul>
        {
          [...error.keys()].map((k) => <li> {error.get(k)} </li>)
        }
      </ul>
    }
  </Box>
}
