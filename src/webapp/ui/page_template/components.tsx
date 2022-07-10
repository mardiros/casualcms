import React from "react";
import { Box, Heading, Icon, Table, TableContainer, Tbody, Td, Th, Thead, Tr } from "@chakra-ui/react";
import { PartialPageTemplate } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/components";
import { Link, useSearchParams } from "react-router-dom";
import { ChevronRightIcon } from "@chakra-ui/icons";


export const TemplateList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [templates, setTemplates] = React.useState<PartialPageTemplate[]>([]);
  const [error, setError] = React.useState<ApiError>(null);
  const [params, setParams] = useSearchParams();
  const parentType = params.get("type");
  const parentPath = params.get("parent");

  React.useEffect(() => {
    async function loadTemplates() {
      const rootTemplates = await config.api.template.listTemplates(token, parentType);
      rootTemplates.
        map((tpls: PartialPageTemplate[]) => setTemplates(tpls)).
        mapErr((err: ApiError) => setError(err));
    }
    loadTemplates();
    setIsLoading(false);
    return function cleanup() { };
  }, []);
  if (isLoading) {
    return (
      <Box>
        Page template Loading...
      </Box>
    )
  }
  const qs = parentPath ? new URLSearchParams({ "parent": parentPath }) : "";
  return (
    <Box>
      {
        templates.length &&
        <>
          <Heading>
            Choose A Type Of Template
          </Heading>
          <Box paddingLeft={15}>
            <TableContainer>
              <Table variant='simple'>
                <Thead>
                  <Tr>
                    <Th>Template Type</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {
                    templates.map(
                      (tpl, i) =>
                        <Tr key={i}>
                          <Td>
                            <Link to={`/admin/page/new/${tpl.type}?${qs}`}>
                              <Icon as={ChevronRightIcon} w={6} h={6} />
                              {tpl.type}
                            </Link>
                          </Td>
                        </Tr>
                    )}
                </Tbody>
              </Table>
            </TableContainer>
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
