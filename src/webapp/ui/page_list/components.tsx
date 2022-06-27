import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { PartialPage } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/components";
import { Link } from "react-router-dom";
export const PageList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [pages, setPages] = React.useState<Array<PartialPage>>([]);
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadRoots() {
      const rootTemplates = await config.api.page.listRoots(token);
      rootTemplates.
        map((tpls) => setPages(tpls)).
        mapErr((err) => setError(err));
    }
    loadRoots();
    return function cleanup() { };
  }, []);
  return (
    <Box>
      {
        pages.length &&
        <>
          <Heading>
            Pages
          </Heading>
          <Box paddingLeft={15}>
            <ul id="page-templates">
              {
                pages.map(
                  (page, i) =>
                    <li key={i}>
                      <Link to={`/admin/page/edit/${page.slug}`}>{page.title}</Link>
                    </li>
                )}
            </ul>
          </Box>
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
