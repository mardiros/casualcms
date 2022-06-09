import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { PartialPageTemplate } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/components";
export const TemplateList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [templates, setTemplates] = React.useState<Array<PartialPageTemplate>>([]);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadRoots() {
      const rootTemplates = await config.api.template.listRoots(token);
      rootTemplates.
        map((tpls) => setTemplates(tpls)).
        mapErr((err) => setError(err));
    }
    loadRoots();
    return function cleanup() { };
  }, []);
  return (
    <Box>
      {
        templates.length &&
        <>
          <Heading>
            Available Templates
          </Heading>
          <ul id="page-templates">
            {templates.map((tpl, i) => <li key={i}>{tpl.type}</li>)}
          </ul>
        </>
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
  );
}
